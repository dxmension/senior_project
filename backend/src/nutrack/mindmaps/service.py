from __future__ import annotations

import asyncio
import io
import json
import uuid
from pathlib import Path

import openai
import pdfplumber

from nutrack.config import settings
from nutrack.mindmaps.exceptions import (
    MindmapGenerationError,
    MindmapNotFoundError,
    MindmapUnavailableError,
)
from nutrack.mindmaps.models import Mindmap
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.mindmaps.schemas import (
    GenerateMindmapRequest,
    MindmapNode,
    SavedMindmapResponse,
)
from nutrack.storage import ObjectStorage
from nutrack.study.models import StudyMaterialUpload
from nutrack.study.repository import StudyMaterialUploadRepository

# Max characters extracted per file and across all files combined
# _MAX_CHARS_PER_FILE = 3_000
# _MAX_TOTAL_CHARS = 10_000

_SYSTEM_PROMPT_WITH_MATERIAL = """\
You are a mindmap generator. Given study material excerpts, produce a JSON mindmap tree.
Rules:
- Root node label should concisely summarize the main topic of the materials (2-6 words)
- Each node has exactly three keys:
    "label": string, 2-6 words
    "description": string, 5-8 sentences — define the concept, explain why it matters, \
describe how it works or relates to surrounding topics, and include any key details or \
examples drawn from the material
    "children": array of child nodes (same structure)
- Max depth: {depth} levels from root
- Cover key subtopics, definitions, and relationships found in the material
- Respond ONLY with valid JSON matching this structure:
  {{"label": "...", "description": "...", "children": [{{"label": "...", "description": "...", "children": []}}]}}
"""

_SYSTEM_PROMPT_NO_MATERIAL = """\
You are a mindmap generator. Produce a JSON mindmap tree for the given week's academic study topics.
Rules:
- Root node label should be a concise academic topic title (2-6 words)
- Each node has exactly three keys:
    "label": string, 2-6 words
    "description": string, 5-8 sentences — define the concept, explain why it matters, \
describe how it works or relates to surrounding topics, and include key examples or details
    "children": array of child nodes (same structure)
- Max depth: {depth} levels from root
- Cover key subtopics, definitions, and relationships
- Respond ONLY with valid JSON matching this structure:
  {{"label": "...", "description": "...", "children": [{{"label": "...", "description": "...", "children": []}}]}}
"""


class MindmapService:
    def __init__(
        self,
        repo: MindmapRepository,
        material_repo: StudyMaterialUploadRepository | None = None,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.repo = repo
        self.material_repo = material_repo
        self.storage = storage or ObjectStorage()

    async def generate_and_save(
        self,
        user_id: int,
        course_id: int,
        request: GenerateMindmapRequest,
    ) -> SavedMindmapResponse:
        if not settings.OPENAI_API_KEY:
            raise MindmapUnavailableError()
        material_text = await self._extract_week_material_text(
            user_id, course_id, request.week
        )
        raw = await self._call_llm(request.week, request.depth, material_text)
        root = self._build_node(raw, depth_remaining=request.depth)
        topic = root.label or f"Week {request.week}"
        mindmap = await self.repo.create(
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            topic=topic,
            tree_json=root.model_dump(),
        )
        return _to_response(mindmap)

    async def list_for_course(
        self, user_id: int, course_id: int
    ) -> list[SavedMindmapResponse]:
        mindmaps = await self.repo.list_by_course_and_user(user_id, course_id)
        return [_to_response(m) for m in mindmaps]

    async def delete(
        self, user_id: int, course_id: int, mindmap_id: int
    ) -> None:
        mindmap = await self.repo.get_by_id_and_user(mindmap_id, user_id)
        if not mindmap or mindmap.course_id != course_id:
            raise MindmapNotFoundError()
        await self.repo.delete(mindmap)

    # Material extraction

    async def _extract_week_material_text(
        self,
        user_id: int,
        course_id: int,
        week: int,
    ) -> str:
        if self.material_repo is None:
            return ""
        uploads = await self.material_repo.list_completed_uploads_for_week(
            user_id, course_id, week
        )
        if not uploads:
            return ""
        parts: list[str] = []
        total = 0
        for upload in uploads:
            # if total >= _MAX_TOTAL_CHARS:
            #     break
            text = await self._extract_text(upload)
            if not text:
                continue
            # truncated = text[:_MAX_CHARS_PER_FILE]
            parts.append(f"[{upload.original_filename}]\n{text}")
            total += len(text)
        return "\n\n".join(parts)

    async def _extract_text(self, upload: StudyMaterialUpload) -> str:
        suffix = Path(upload.original_filename).suffix.lower()
        if suffix != ".pdf":
            return ""
        try:
            data = await self.storage.download_file_bytes(upload.storage_key)
            return await asyncio.to_thread(_extract_pdf_text, data)
        except Exception:
            return ""

    # LLM call

    async def _call_llm(self, week: int, depth: int, material_text: str) -> dict:
        client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        if material_text:
            system = _SYSTEM_PROMPT_WITH_MATERIAL.format(depth=depth)
            user_msg = (
                f"Study material from Week {week}:\n{material_text}\n\n"
                "Generate a mindmap grounded in these materials."
            )
        else:
            system = _SYSTEM_PROMPT_NO_MATERIAL.format(depth=depth)
            user_msg = f"Generate a mindmap for Week {week} study topics."
        try:
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_msg},
                ],
            )
            return json.loads(response.choices[0].message.content)
        except Exception as exc:
            raise MindmapGenerationError(str(exc)) from exc

    def _build_node(self, raw: dict, depth_remaining: int) -> MindmapNode:
        children: list[MindmapNode] = []
        if depth_remaining > 1:
            children = [
                self._build_node(child, depth_remaining - 1)
                for child in raw.get("children", [])
            ]
        return MindmapNode(
            id=uuid.uuid4().hex[:12],
            label=raw.get("label", ""),
            description=raw.get("description", ""),
            children=children,
        )


def _extract_pdf_text(data: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                text_parts.append(page_text.strip())
    return "\n".join(text_parts)


def _to_response(mindmap: Mindmap) -> SavedMindmapResponse:
    root = MindmapNode.model_validate(mindmap.tree_json)
    return SavedMindmapResponse(
        id=mindmap.id,
        course_id=mindmap.course_id,
        week=mindmap.week,
        topic=mindmap.topic,
        root=root,
        created_at=mindmap.created_at,
    )
