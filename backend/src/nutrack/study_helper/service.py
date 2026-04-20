from __future__ import annotations

import asyncio
import hashlib
import io
from pathlib import Path

import pdfplumber

from nutrack.course_materials.models import CourseMaterialUpload
from nutrack.course_materials.repository import CourseMaterialUploadRepository
from nutrack.logging import get_logger, log_step
from nutrack.mindmaps.models import Mindmap
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.storage import ObjectStorage
from nutrack.study_helper.exceptions import (
    StudyGuideGenerationError,
    StudyGuideNotFoundError,
    StudyGuideUnavailableError,
)
from nutrack.study_helper.models import (
    StudyGuide,
    StudyGuideSourceType,
    WeekOverviewCache,
)
from nutrack.study_helper.repository import (
    StudyGuideRepository,
    WeekOverviewCacheRepository,
)
from nutrack.study_helper.schemas import (
    DeepDiveLLMResponse,
    DeepDiveResponse,
    DetailLLMResponse,
    DetailResponse,
    KeyPoint,
    OverviewLLMResponse,
    StudyGuideOverview,
    StudyGuideResponse,
    TopicExtractionLLMResponse,
    TopicItem,
    TopicListResponse,
    WeekOverviewResponse,
    WeekSummaryLLMResponse,
)
from nutrack.tools.llm import (
    LLMConfigurationError,
    LLMError,
    parse_structured_response,
)

MAX_SOURCE_TEXT_CHARS = 20_000
MAX_FILE_TEXT_CHARS = 8_000
logger = get_logger(__name__)

_OVERVIEW_SYSTEM_PROMPT_MATERIALS = """\
You are a study guide generator. Given study material excerpts, produce a \
structured study guide.
Rules:
- Summarize the topic in 2-3 sentences.
- Identify 5 key points from the material.
- Each key point needs: id (short unique string), label (2-6 words), \
short_description (1-2 sentences).
- Ground all content in the provided material.
"""

_OVERVIEW_SYSTEM_PROMPT_AI = """\
You are a study guide generator. Produce a structured study guide for the \
given academic topic.
Rules:
- Summarize the topic in 2-3 sentences.
- Identify 5 key points.
- Each key point needs: id (short unique string), label (2-6 words), \
short_description (1-2 sentences).
- Use accurate academic knowledge.
"""

_DETAIL_SYSTEM_PROMPT = """\
Given a key point from a study guide, provide a detailed explanation in \
3 paragraphs. Cover definitions, relationships, and practical implications.\
"""

_DEEP_EXPLAIN_SYSTEM_PROMPT = """\
Provide a deeper, more nuanced explanation of this concept. Include edge \
cases, common misconceptions, and connections to related topics.\
"""

_DEEP_EXAMPLE_SYSTEM_PROMPT = """\
Provide 2-3 concrete, practical examples that illustrate this concept. \
Include step-by-step reasoning where applicable.\
"""

_TOPIC_EXTRACTION_SYSTEM_PROMPT = """\
Given study material text, extract a list of distinct academic topics \
covered. Return 5-10 topic names, each 2-8 words. Be specific and \
descriptive. No duplicates.\
"""

_WEEK_SUMMARY_SYSTEM_PROMPT_MATERIALS = """\
You are a study assistant. Given study material excerpts for a specific \
week, produce:
1. A concise 2-4 sentence summary of what this week covers.
2. A list of 4-8 distinct topics found in the materials, each 2-8 words.
Ground everything in the provided material.\
"""

_WEEK_SUMMARY_SYSTEM_PROMPT_AI = """\
You are a study assistant. Given a course and week number, produce:
1. A concise 2-4 sentence summary of what a typical week at this point \
in the course might cover.
2. A list of 4-8 likely academic topics for this week, each 2-8 words.
Use general academic knowledge.\
"""


class StudyHelperService:
    def __init__(
        self,
        repo: StudyGuideRepository,
        week_cache_repo: WeekOverviewCacheRepository,
        mindmap_repo: MindmapRepository | None = None,
        material_repo: CourseMaterialUploadRepository | None = None,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.repo = repo
        self.week_cache_repo = week_cache_repo
        self.mindmap_repo = mindmap_repo
        self.material_repo = material_repo
        self.storage = storage or ObjectStorage()

    async def list_topics(
        self,
        user_id: int,
        course_id: int,
        week: int,
    ) -> TopicListResponse:
        topics: list[TopicItem] = []
        seen: set[str] = set()

        if self.mindmap_repo:
            mindmaps = await self.mindmap_repo.list_by_course_and_user(
                user_id, course_id
            )
            for mm in mindmaps:
                if mm.week == week:
                    _add_mindmap_topics(mm, topics, seen)

        if self.material_repo:
            material_text = await _extract_week_material_text(
                self.material_repo, self.storage, user_id, course_id, week
            )
            if material_text:
                extracted = await _extract_topics_from_text(material_text)
                for name in extracted:
                    lower = name.lower().strip()
                    if lower not in seen:
                        seen.add(lower)
                        topics.append(TopicItem(name=name, source="material"))

        return TopicListResponse(topics=topics)

    async def generate_week_overview(
        self,
        user_id: int,
        course_id: int,
        week: int,
    ) -> WeekOverviewResponse:
        uploads: list[CourseMaterialUpload] = []
        if self.material_repo:
            uploads = await self.material_repo.list_completed_uploads_for_week(
                user_id, course_id, week
            )
        meta_hash = _compute_metadata_hash(uploads)
        has_materials = bool(uploads)

        cached = await self.week_cache_repo.find_cached(
            user_id, course_id, week
        )
        if cached and _hash_matches(cached.materials_hash, meta_hash):
            return await _week_cache_to_response(
                cached, self.mindmap_repo, user_id, course_id, has_materials
            )

        # Only generate content if materials exist
        if not has_materials:
            # Create cache entry with empty summary and topics for weeks without materials
            if cached:
                await self.week_cache_repo.update(
                    cached,
                    summary="",
                    topics_json=[],
                    materials_hash=meta_hash,
                )
                entry = cached
            else:
                entry = await self.week_cache_repo.create(
                    user_id=user_id,
                    course_id=course_id,
                    week=week,
                    summary="",
                    topics_json=[],
                    materials_hash=meta_hash,
                )
        else:
            material_text = await _extract_uploads_text(self.storage, uploads)
            week_data = await _generate_week_summary(week, material_text)

            llm_topics = [
                {"name": t, "source": "material"} for t in week_data.topics
            ]

            if cached:
                await self.week_cache_repo.update(
                    cached,
                    summary=week_data.summary,
                    topics_json=llm_topics,
                    materials_hash=meta_hash,
                )
                entry = cached
            else:
                entry = await self.week_cache_repo.create(
                    user_id=user_id,
                    course_id=course_id,
                    week=week,
                    summary=week_data.summary,
                    topics_json=llm_topics,
                    materials_hash=meta_hash,
                )

        return await _week_cache_to_response(
            entry, self.mindmap_repo, user_id, course_id, has_materials
        )

    async def warm_cache(
        self,
        user_id: int,
        course_id: int,
    ) -> list[int]:
        if not self.material_repo:
            return []
        refreshed: list[int] = []
        all_uploads = await self.material_repo.list_user_uploads(
            user_id, course_id
        )
        completed = [
            u for u in all_uploads if u.upload_status.value == "completed"
        ]
        by_week: dict[int, list[CourseMaterialUpload]] = {}
        for u in completed:
            by_week.setdefault(u.user_week, []).append(u)

        for week in sorted(by_week):
            week_uploads = by_week[week]
            meta_hash = _compute_metadata_hash(week_uploads)
            cached = await self.week_cache_repo.find_cached(
                user_id, course_id, week
            )
            if cached and _hash_matches(cached.materials_hash, meta_hash):
                continue
            
            has_materials = bool(week_uploads)
            
            # Only generate content if materials exist
            if not has_materials:
                # Create cache entry with empty summary and topics for weeks without materials
                if cached:
                    await self.week_cache_repo.update(
                        cached,
                        summary="",
                        topics_json=[],
                        materials_hash=meta_hash,
                    )
                else:
                    await self.week_cache_repo.create(
                        user_id=user_id,
                        course_id=course_id,
                        week=week,
                        summary="",
                        topics_json=[],
                        materials_hash=meta_hash,
                    )
                refreshed.append(week)
                continue
                
            material_text = await _extract_uploads_text(
                self.storage, week_uploads
            )
            try:
                week_data = await _generate_week_summary(week, material_text)
            except (StudyGuideGenerationError, StudyGuideUnavailableError):
                log_step(
                    logger,
                    "study_helper_warm_cache_failed",
                    user_id=user_id,
                    course_id=course_id,
                    week=week,
                )
                continue
            llm_topics = [
                {"name": t, "source": "material"} for t in week_data.topics
            ]
            if cached:
                await self.week_cache_repo.update(
                    cached,
                    summary=week_data.summary,
                    topics_json=llm_topics,
                    materials_hash=meta_hash,
                )
            else:
                await self.week_cache_repo.create(
                    user_id=user_id,
                    course_id=course_id,
                    week=week,
                    summary=week_data.summary,
                    topics_json=llm_topics,
                    materials_hash=meta_hash,
                )
            refreshed.append(week)
        return refreshed

    async def generate_overview(
        self,
        user_id: int,
        course_id: int,
        topic: str,
        week: int | None = None,
    ) -> StudyGuideResponse:
        uploads: list[CourseMaterialUpload] = []
        if self.material_repo:
            if week is not None:
                uploads = await self.material_repo.list_completed_uploads_for_week(
                    user_id, course_id, week
                )
            else:
                all_up = await self.material_repo.list_user_uploads(
                    user_id, course_id
                )
                uploads = [
                    u for u in all_up if u.upload_status.value == "completed"
                ]

        meta_hash = _compute_metadata_hash(uploads)

        cached = await self.repo.find_cached(user_id, course_id, topic)
        if cached and _hash_matches(cached.materials_hash, meta_hash):
            return _to_response(cached)

        material_text = await _extract_uploads_text(self.storage, uploads) if uploads else ""
        overview = await _generate_overview(topic, material_text)
        source_type = _determine_source_type(material_text)

        if cached:
            guide = await self.repo.update(
                cached,
                overview_json=overview.model_dump(),
                details_json={},
                source_type=source_type,
                materials_hash=meta_hash,
            )
        else:
            guide = await self.repo.create(
                user_id=user_id,
                course_id=course_id,
                topic=topic,
                overview_json=overview.model_dump(),
                details_json={},
                source_type=source_type,
                materials_hash=meta_hash,
            )

        return _to_response(guide)

    async def get_guide(
        self,
        user_id: int,
        guide_id: int,
    ) -> StudyGuideResponse:
        guide = await self.repo.get_by_id_and_user(guide_id, user_id)
        if not guide:
            raise StudyGuideNotFoundError()
        return _to_response(guide)

    async def generate_detail(
        self,
        user_id: int,
        guide_id: int,
        point_id: str,
    ) -> DetailResponse:
        guide = await self.repo.get_by_id_and_user(guide_id, user_id)
        if not guide:
            raise StudyGuideNotFoundError()

        details: dict = dict(guide.details_json)
        existing = details.get(point_id)
        if existing and isinstance(existing, dict) and existing.get("explanation"):
            return DetailResponse(
                point_id=point_id,
                explanation=existing["explanation"],
            )

        point = _find_point(guide.overview_json, point_id)
        overview_ctx = guide.overview_json.get("summary", "")
        explanation = await _generate_detail(point, overview_ctx)

        if point_id not in details:
            details[point_id] = {}
        details[point_id]["explanation"] = explanation
        await self.repo.update(guide, details_json=details)

        return DetailResponse(point_id=point_id, explanation=explanation)

    async def generate_deep_dive(
        self,
        user_id: int,
        guide_id: int,
        point_id: str,
        dive_type: str,
    ) -> DeepDiveResponse:
        guide = await self.repo.get_by_id_and_user(guide_id, user_id)
        if not guide:
            raise StudyGuideNotFoundError()

        details: dict = dict(guide.details_json)
        point_data = details.get(point_id, {})
        if isinstance(point_data, dict) and point_data.get(dive_type):
            return DeepDiveResponse(
                point_id=point_id,
                dive_type=dive_type,
                content=point_data[dive_type],
            )

        point = _find_point(guide.overview_json, point_id)
        explanation = point_data.get("explanation", "") if isinstance(point_data, dict) else ""
        content = await _generate_deep_dive(point, explanation, dive_type)

        if point_id not in details:
            details[point_id] = {}
        details[point_id][dive_type] = content
        await self.repo.update(guide, details_json=details)

        return DeepDiveResponse(
            point_id=point_id,
            dive_type=dive_type,
            content=content,
        )

    async def delete_guide(
        self,
        user_id: int,
        course_id: int,
        guide_id: int,
    ) -> None:
        guide = await self.repo.get_by_id_and_user(guide_id, user_id)
        if not guide or guide.course_id != course_id:
            raise StudyGuideNotFoundError()
        await self.repo.delete(guide)


def _add_mindmap_topics(
    mm: Mindmap,
    topics: list[TopicItem],
    seen: set[str],
) -> None:
    tree = mm.tree_json
    if not isinstance(tree, dict):
        return
    label = tree.get("label", "")
    if label:
        lower = label.lower().strip()
        if lower not in seen:
            seen.add(lower)
            topics.append(TopicItem(name=label, source="mindmap"))
    for child in tree.get("children", []):
        child_label = child.get("label", "") if isinstance(child, dict) else ""
        if child_label:
            lower = child_label.lower().strip()
            if lower not in seen:
                seen.add(lower)
                topics.append(TopicItem(name=child_label, source="mindmap"))


def _find_point(overview_json: dict, point_id: str) -> dict:
    for kp in overview_json.get("key_points", []):
        if kp.get("id") == point_id:
            return kp
    raise StudyGuideNotFoundError()


def _hash_matches(stored: str | None, current: str | None) -> bool:
    if stored is None and current is None:
        return True
    if stored is None or current is None:
        return False
    return stored == current


async def _week_cache_to_response(
    entry: WeekOverviewCache,
    mindmap_repo: MindmapRepository | None,
    user_id: int,
    course_id: int,
    has_materials: bool | None = None,
) -> WeekOverviewResponse:
    topics: list[TopicItem] = []
    seen: set[str] = set()

    if mindmap_repo:
        mindmaps = await mindmap_repo.list_by_course_and_user(
            user_id, course_id
        )
        for mm in mindmaps:
            if mm.week == entry.week:
                _add_mindmap_topics(mm, topics, seen)

    for t in entry.topics_json:
        name = t.get("name", "") if isinstance(t, dict) else str(t)
        lower = name.lower().strip()
        if lower and lower not in seen:
            seen.add(lower)
            source = t.get("source", "material") if isinstance(t, dict) else "material"
            topics.append(TopicItem(name=name, source=source))

    resolved_has_materials = (
        has_materials
        if has_materials is not None
        else entry.materials_hash is not None
    )

    return WeekOverviewResponse(
        week=entry.week,
        summary=entry.summary,
        topics=topics,
        has_materials=resolved_has_materials,
    )


def _cache_valid(guide: StudyGuide, current_hash: str | None) -> bool:
    if current_hash is None and guide.materials_hash is None:
        return True
    if current_hash is None or guide.materials_hash is None:
        return False
    return guide.materials_hash == current_hash


def _compute_hash(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def _compute_metadata_hash(
    uploads: list[CourseMaterialUpload],
) -> str | None:
    if not uploads:
        return None
    parts = sorted(
        f"{u.id}:{u.updated_at.isoformat()}" for u in uploads
    )
    return hashlib.sha256("|".join(parts).encode()).hexdigest()


def _determine_source_type(material_text: str) -> StudyGuideSourceType:
    if material_text:
        return StudyGuideSourceType.HYBRID
    return StudyGuideSourceType.AI_KNOWLEDGE


def _to_response(guide: StudyGuide) -> StudyGuideResponse:
    overview = StudyGuideOverview.model_validate(guide.overview_json)
    return StudyGuideResponse(
        id=guide.id,
        topic=guide.topic,
        source_type=guide.source_type.value,
        overview=overview,
        details=guide.details_json,
        created_at=guide.created_at,
    )


def _extract_pdf_text(data: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                text_parts.append(page_text.strip())
    return "\n".join(text_parts)


async def _extract_uploads_text(
    storage: ObjectStorage,
    uploads: list[CourseMaterialUpload],
) -> str:
    parts: list[str] = []
    for upload in uploads:
        text = await _extract_file_text(storage, upload)
        if text:
            parts.append(f"[{upload.original_filename}]\n{text}")
    combined = "\n\n".join(parts)
    return combined[:MAX_SOURCE_TEXT_CHARS].strip()


async def _extract_week_material_text(
    material_repo: CourseMaterialUploadRepository,
    storage: ObjectStorage,
    user_id: int,
    course_id: int,
    week: int,
) -> str:
    uploads = await material_repo.list_completed_uploads_for_week(
        user_id, course_id, week
    )
    if not uploads:
        return ""
    parts: list[str] = []
    for upload in uploads:
        text = await _extract_file_text(storage, upload)
        if text:
            parts.append(f"[{upload.original_filename}]\n{text}")
    combined = "\n\n".join(parts)
    return combined[:MAX_SOURCE_TEXT_CHARS].strip()


async def _extract_all_material_text(
    material_repo: CourseMaterialUploadRepository,
    storage: ObjectStorage,
    user_id: int,
    course_id: int,
) -> str:
    uploads = await material_repo.list_user_uploads(user_id, course_id)
    completed = [
        u for u in uploads if u.upload_status.value == "completed"
    ]
    if not completed:
        return ""
    parts: list[str] = []
    for upload in completed:
        text = await _extract_file_text(storage, upload)
        if text:
            parts.append(f"[{upload.original_filename}]\n{text}")
    combined = "\n\n".join(parts)
    return combined[:MAX_SOURCE_TEXT_CHARS].strip()


async def _extract_file_text(
    storage: ObjectStorage,
    upload: CourseMaterialUpload,
) -> str:
    suffix = Path(upload.original_filename).suffix.lower()
    if suffix != ".pdf":
        return ""
    try:
        data = await storage.download_file_bytes(upload.storage_key)
        text = await asyncio.to_thread(_extract_pdf_text, data)
        return text[:MAX_FILE_TEXT_CHARS].strip()
    except Exception as exc:
        log_step(
            logger,
            "study_helper_material_extract_failed",
            filename=upload.original_filename,
            error=str(exc),
        )
        return ""


async def _extract_topics_from_text(material_text: str) -> list[str]:
    try:
        response = await parse_structured_response(
            system_prompt=_TOPIC_EXTRACTION_SYSTEM_PROMPT,
            user_prompt=f"Extract topics from:\n{material_text[:8000]}",
            response_model=TopicExtractionLLMResponse,
            max_output_tokens=500,
        )
        return response.topics
    except (LLMConfigurationError, LLMError) as exc:
        log_step(logger, "study_helper_topic_extraction_failed", error=str(exc))
        return []


async def _generate_overview(
    topic: str,
    material_text: str,
) -> OverviewLLMResponse:
    if material_text:
        system_prompt = _OVERVIEW_SYSTEM_PROMPT_MATERIALS
        user_prompt = (
            f"Topic: {topic}\n\n"
            f"Study materials:\n{material_text}\n\n"
            "Generate a study guide focused on this topic."
        )
    else:
        system_prompt = _OVERVIEW_SYSTEM_PROMPT_AI
        user_prompt = f"Generate a study guide for: {topic}"

    try:
        return await parse_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=OverviewLLMResponse,
            max_output_tokens=1_500,
        )
    except LLMConfigurationError as exc:
        raise StudyGuideUnavailableError() from exc
    except LLMError as exc:
        raise StudyGuideGenerationError(str(exc)) from exc


async def _generate_detail(
    point: dict,
    overview_context: str,
) -> str:
    user_prompt = (
        f"Study guide context: {overview_context}\n\n"
        f"Key point: {point.get('label', '')}\n"
        f"Description: {point.get('short_description', '')}\n\n"
        "Provide a detailed explanation."
    )
    try:
        response = await parse_structured_response(
            system_prompt=_DETAIL_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=DetailLLMResponse,
            max_output_tokens=1_000,
        )
        return response.explanation
    except LLMConfigurationError as exc:
        raise StudyGuideUnavailableError() from exc
    except LLMError as exc:
        raise StudyGuideGenerationError(str(exc)) from exc


async def _generate_deep_dive(
    point: dict,
    existing_explanation: str,
    dive_type: str,
) -> str:
    system_prompt = (
        _DEEP_EXPLAIN_SYSTEM_PROMPT
        if dive_type == "explain_more"
        else _DEEP_EXAMPLE_SYSTEM_PROMPT
    )
    user_prompt = (
        f"Key point: {point.get('label', '')}\n"
        f"Description: {point.get('short_description', '')}\n"
        f"Previous explanation: {existing_explanation}\n\n"
        f"{'Explain further.' if dive_type == 'explain_more' else 'Give examples.'}"
    )
    try:
        response = await parse_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=DeepDiveLLMResponse,
            max_output_tokens=1_000,
        )
        return response.content
    except LLMConfigurationError as exc:
        raise StudyGuideUnavailableError() from exc
    except LLMError as exc:
        raise StudyGuideGenerationError(str(exc)) from exc


async def _generate_week_summary(
    week: int,
    material_text: str,
) -> WeekSummaryLLMResponse:
    if material_text:
        system_prompt = _WEEK_SUMMARY_SYSTEM_PROMPT_MATERIALS
        user_prompt = (
            f"Week {week} study materials:\n{material_text}\n\n"
            "Summarize this week and extract topics."
        )
    else:
        system_prompt = _WEEK_SUMMARY_SYSTEM_PROMPT_AI
        user_prompt = f"Generate a week summary and topics for Week {week}."

    try:
        return await parse_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=WeekSummaryLLMResponse,
            max_output_tokens=800,
        )
    except LLMConfigurationError as exc:
        raise StudyGuideUnavailableError() from exc
    except LLMError as exc:
        raise StudyGuideGenerationError(str(exc)) from exc
