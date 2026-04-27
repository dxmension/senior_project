import asyncio
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.assessments.models import Assessment, AssessmentType
from nutrack.config import settings
from nutrack.courses.models import Course, CourseOffering
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.flashcards.models import (
    FlashcardDeck,
    FlashcardSession,
    FlashcardSessionCard,
    FlashcardSessionStatus,
)
from nutrack.insights.schemas import InsightLLMResponse, InsightsResponse
from nutrack.mindmaps.models import Mindmap
from nutrack.mock_exams.models import (
    MockExam,
    MockExamAttempt,
    MockExamAttemptStatus,
    MockExamVisibilityScope,
)
from nutrack.tools.llm.service import parse_structured_response
from nutrack.users.models import User

_CACHE_TTL = 86400
_MAX_PROMPT_CHARS = 2000
_CACHE_PREFIX = "ai_insights"
_LOCK_PREFIX = "ai_insights_lock"
_WEAK_SCORE_PCT = 70.0
_WEAK_MOCK_PCT = 60.0
_ALLOWED_ACTION_TYPES = {AssessmentType.QUIZ.value, AssessmentType.MIDTERM.value}
_LOCK_TTL = 120
_LOCK_WAIT_SECONDS = 12
_LOCK_POLL_SECONDS = 0.25
_SYSTEM_PROMPT = """
You are an academic performance coach for university students.

Return structured JSON only.

Rules:
- short_summary: 2-3 sentences, start with a motivational sentence using the student's first name.
- long_summary: exactly 4-5 sentences separated by blank lines.
- Sentence 1: motivational opener using the student's first name and major.
- Sentence 2: performance analysis using real numbers from the prompt.
- Sentence 3: weak areas, especially courses or assessment types below 70%, or mock results below 60%.
- Sentence 4 if useful: a concrete focus plan for the next 7 days.
- actions: 2-4 items, prioritize the weakest areas first.
- make in bullet point, very concise.
- Every action_url must be a real route from the provided options and must start with /study/.
- If no valid action routes are available, return an empty actions list.
- Use only course IDs, assessment types, and assessment numbers that appear in the prompt.
- Keep the tone specific, and practical.
""".strip()


def _cache_key(user_id: int) -> str:
    return f"{_CACHE_PREFIX}:{user_id}"


def _lock_key(user_id: int) -> str:
    return f"{_LOCK_PREFIX}:{user_id}"


def _course_code(course: Course) -> str:
    level = (course.level or "").strip()
    return f"{course.code} {level}" if level and level != "0" else course.code


def _safe_pct(score: float | None, max_score: float | None) -> float | None:
    if score is None or max_score in (None, 0):
        return None
    return round(score / max_score * 100, 1)


def _avg_pct(values: list[float]) -> float | None:
    return round(mean(values), 1) if values else None


def _trim(text: str, max_chars: int = _MAX_PROMPT_CHARS) -> str:
    stripped = text.strip()
    return stripped if len(stripped) <= max_chars else stripped[: max_chars - 1].rstrip() + "…"


def _study_year_label(study_year: int | None, total_years: int | None) -> str:
    if study_year is None or total_years is None:
        return "unknown"
    return f"{study_year}/{total_years}"


def _infer_total_years(user: User) -> int | None:
    if user.study_year is None and user.enrollment_year is None:
        return None
    base_years = 4
    if user.study_year is None:
        return base_years
    return max(base_years, user.study_year)


def _render_lines(title: str, lines: list[str]) -> str:
    body = "; ".join(lines) if lines else "none"
    return f"{title}: {body}"


def _format_course_summary(item: dict[str, Any]) -> str:
    score = item["assessment_avg_pct"]
    mock = item["mock_avg_pct"]
    overdue = item["overdue_count"]
    metadata = item["study_metadata"]
    return (
        f'{item["course_code"]} {item["course_title"]} ({item["course_id"]}) '
        f'ects={item["ects"]} '
        f'assess={score if score is not None else "n/a"}% '
        f'mocks={mock if mock is not None else "n/a"}% '
        f'overdue={overdue} '
        f'available[mock={metadata["mock_exam_count"]}, '
        f'flashcards={metadata["flashcard_deck_count"]}, '
        f'mindmaps={metadata["mindmap_count"]}]'
    )


def _format_overdue_item(item: dict[str, Any]) -> str:
    return (
        f'{item["course_code"]} {item["assessment_type"]} {item["assessment_number"]} '
        f'{item["days_overdue"]}d overdue'
    )


def _format_flashcard_item(item: dict[str, Any]) -> str:
    return (
        f'{item["course_code"]} "{item["deck_title"]}" '
        f'hard={item["hard_rate"]}% seen={item["times_seen"]}'
    )


def _format_history_item(item: dict[str, Any]) -> str:
    return f'{item["course_code"]} {item["grade"]} ({item["grade_points"]})'


def _candidate_actions(context: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    for item in context["courses"]:
        for route in item["route_options"]:
            lines.append(
                f'{route["action_type"]}: {route["label"]} -> {route["action_url"]}'
            )
    return lines


def _allowed_action_urls(context: dict[str, Any]) -> set[str]:
    urls: set[str] = set()
    for course in context["courses"]:
        for route in course["route_options"]:
            urls.add(route["action_url"])
    return urls


def _sanitize_actions(
    payload: InsightLLMResponse,
    context: dict[str, Any],
) -> InsightLLMResponse:
    allowed_urls = _allowed_action_urls(context)
    actions = [
        item for item in payload.actions if item.action_url in allowed_urls
    ]
    return InsightLLMResponse(
        short_summary=payload.short_summary.strip(),
        long_summary=payload.long_summary.strip(),
        actions=actions[:4],
    )


def _response_from_llm(
    payload: InsightLLMResponse,
    generated_at: datetime,
    *,
    cached: bool,
) -> InsightsResponse:
    return InsightsResponse(
        short_summary=payload.short_summary,
        long_summary=payload.long_summary,
        actions=payload.actions,
        generated_at=generated_at,
        cached=cached,
    )


def _build_user_prompt(context: dict[str, Any]) -> str:
    student = context["student"]
    course_lines = [_format_course_summary(item) for item in context["courses"]]
    overdue_lines = [_format_overdue_item(item) for item in context["overdue_items"][:4]]
    flashcard_lines = [_format_flashcard_item(item) for item in context["flashcards"][:4]]
    history_lines = [_format_history_item(item) for item in context["history"][:5]]
    weak_lines = context["weak_signals"][:6] or ["none"]
    action_lines = _candidate_actions(context)[:12]
    prompt = "\n".join(
        [
            (
                f'Student: {student["first_name"]}; major={student["major"]}; '
                f'cgpa={student["cgpa"]}; study_year={student["study_year"]}; '
                f'total_years={student["total_years"]}; '
                f'study_progress={student["study_progress"]}; '
                f'current_term={student["term"]} {student["year"]}'
            ),
            _render_lines("Current courses", course_lines),
            _render_lines("Weak signals", weak_lines),
            _render_lines("Overdue", overdue_lines),
            _render_lines("Recent flashcards", flashcard_lines),
            _render_lines("Passed history", history_lines),
            _render_lines("Allowed actions", action_lines),
        ]
    )
    return _trim(prompt)


class InsightsService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis

    async def get_or_generate(self, user_id: int, user: User) -> InsightsResponse:
        cached = await self.redis.get(_cache_key(user_id))
        if cached:
            payload = InsightsResponse.model_validate_json(cached)
            return payload.model_copy(update={"cached": True})
        if not await self._acquire_lock(user_id):
            return await self._wait_for_cached_result(user_id, user)
        try:
            latest = await self.redis.get(_cache_key(user_id))
            if latest:
                payload = InsightsResponse.model_validate_json(latest)
                return payload.model_copy(update={"cached": True})
            payload = await self._generate_insights(user_id, user)
            await self.redis.setex(
                _cache_key(user_id),
                _CACHE_TTL,
                payload.model_dump_json(),
            )
            return payload
        finally:
            await self.redis.delete(_lock_key(user_id))

    async def _acquire_lock(self, user_id: int) -> bool:
        return bool(
            await self.redis.set(
                _lock_key(user_id),
                "1",
                ex=_LOCK_TTL,
                nx=True,
            )
        )

    async def _wait_for_cached_result(
        self,
        user_id: int,
        user: User,
    ) -> InsightsResponse:
        attempts = int(_LOCK_WAIT_SECONDS / _LOCK_POLL_SECONDS)
        for _ in range(attempts):
            await asyncio.sleep(_LOCK_POLL_SECONDS)
            cached = await self.redis.get(_cache_key(user_id))
            if cached:
                payload = InsightsResponse.model_validate_json(cached)
                return payload.model_copy(update={"cached": True})
            if not await self.redis.exists(_lock_key(user_id)):
                return await self.get_or_generate(user_id, user)
        return await self.get_or_generate(user_id, user)

    async def _generate_insights(self, user_id: int, user: User) -> InsightsResponse:
        context = await self._aggregate_context(user_id, user)
        llm_payload = await parse_structured_response(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=_build_user_prompt(context),
            response_model=InsightLLMResponse,
            model="gpt-4o-mini",
            temperature=0.2,
        )
        generated_at = datetime.now(timezone.utc)
        sanitized = _sanitize_actions(llm_payload, context)
        return _response_from_llm(sanitized, generated_at, cached=False)

    async def _aggregate_context(self, user_id: int, user: User) -> dict[str, Any]:
        enrollments, history, assessments, attempts, sessions, study_metadata = (
            await asyncio.gather(
            self._fetch_current_enrollments(user_id),
            self._fetch_passed_history(user_id),
            self._fetch_assessments(user_id),
            self._fetch_mock_attempts(user_id),
            self._fetch_flashcard_sessions(user_id),
            self._fetch_study_metadata(user_id),
        )
        )
        return _build_context(
            user,
            enrollments,
            history,
            assessments,
            attempts,
            sessions,
            study_metadata,
        )

    async def _fetch_current_enrollments(self, user_id: int) -> list[Enrollment]:
        stmt = (
            select(Enrollment)
            .options(
                joinedload(Enrollment.course_offering).joinedload(CourseOffering.course)
            )
            .where(Enrollment.user_id == user_id)
            .where(Enrollment.status == EnrollmentStatus.IN_PROGRESS)
            .where(Enrollment.term == settings.CURRENT_TERM)
            .where(Enrollment.year == settings.CURRENT_YEAR)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_passed_history(self, user_id: int) -> list[Enrollment]:
        stmt = (
            select(Enrollment)
            .options(
                joinedload(Enrollment.course_offering).joinedload(CourseOffering.course)
            )
            .where(Enrollment.user_id == user_id)
            .where(Enrollment.status == EnrollmentStatus.PASSED)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_assessments(self, user_id: int) -> list[Assessment]:
        course_ids = await self._current_course_ids(user_id)
        if not course_ids:
            return []
        stmt = (
            select(Assessment)
            .options(
                joinedload(Assessment.course_offering).joinedload(CourseOffering.course)
            )
            .where(Assessment.user_id == user_id)
            .where(Assessment.course_id.in_(course_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_mock_attempts(self, user_id: int) -> list[MockExamAttempt]:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = (
            select(MockExamAttempt)
            .options(joinedload(MockExamAttempt.mock_exam))
            .where(MockExamAttempt.user_id == user_id)
            .where(MockExamAttempt.status == MockExamAttemptStatus.COMPLETED)
            .where(MockExamAttempt.submitted_at >= since)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_flashcard_sessions(self, user_id: int) -> list[FlashcardSession]:
        since = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = (
            select(FlashcardSession)
            .options(
                joinedload(FlashcardSession.deck),
                joinedload(FlashcardSession.session_cards).joinedload(
                    FlashcardSessionCard.flashcard
                ),
            )
            .where(FlashcardSession.user_id == user_id)
            .where(FlashcardSession.status == FlashcardSessionStatus.COMPLETED.value)
            .where(FlashcardSession.completed_at >= since)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _current_course_ids(self, user_id: int) -> list[int]:
        stmt = (
            select(Enrollment.course_id)
            .where(Enrollment.user_id == user_id)
            .where(Enrollment.status == EnrollmentStatus.IN_PROGRESS)
            .where(Enrollment.term == settings.CURRENT_TERM)
            .where(Enrollment.year == settings.CURRENT_YEAR)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _fetch_study_metadata(self, user_id: int) -> dict[int, dict[str, Any]]:
        course_ids = await self._current_course_ids(user_id)
        if not course_ids:
            return {}
        mock_exams, decks, mindmaps = await asyncio.gather(
            self._fetch_visible_mock_exams(user_id, course_ids),
            self._fetch_flashcard_decks(user_id, course_ids),
            self._fetch_mindmaps(user_id, course_ids),
        )
        metadata = {
            course_id: {
                "mock_exam_count": 0,
                "mock_families": set(),
                "flashcard_deck_count": 0,
                "mindmap_count": 0,
            }
            for course_id in course_ids
        }
        for exam in mock_exams:
            item = metadata.setdefault(
                exam.course_id,
                {
                    "mock_exam_count": 0,
                    "mock_families": set(),
                    "flashcard_deck_count": 0,
                    "mindmap_count": 0,
                },
            )
            item["mock_exam_count"] += 1
            item["mock_families"].add(
                (exam.assessment_type.value, exam.assessment_number)
            )
        for deck in decks:
            metadata.setdefault(deck.course_id, _empty_study_metadata())
            metadata[deck.course_id]["flashcard_deck_count"] += 1
        for mindmap in mindmaps:
            metadata.setdefault(mindmap.course_id, _empty_study_metadata())
            metadata[mindmap.course_id]["mindmap_count"] += 1
        return metadata

    async def _fetch_visible_mock_exams(
        self,
        user_id: int,
        course_ids: list[int],
    ) -> list[MockExam]:
        stmt = (
            select(MockExam)
            .where(MockExam.course_id.in_(course_ids))
            .where(MockExam.is_active.is_(True))
            .where(
                (
                    MockExam.visibility_scope == MockExamVisibilityScope.COURSE
                ) | (MockExam.owner_user_id == user_id)
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _fetch_flashcard_decks(
        self,
        user_id: int,
        course_ids: list[int],
    ) -> list[FlashcardDeck]:
        stmt = (
            select(FlashcardDeck)
            .where(FlashcardDeck.owner_user_id == user_id)
            .where(FlashcardDeck.course_id.in_(course_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def _fetch_mindmaps(
        self,
        user_id: int,
        course_ids: list[int],
    ) -> list[Mindmap]:
        stmt = (
            select(Mindmap)
            .where(Mindmap.user_id == user_id)
            .where(Mindmap.course_id.in_(course_ids))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


def _empty_study_metadata() -> dict[str, Any]:
    return {
        "mock_exam_count": 0,
        "mock_families": set(),
        "flashcard_deck_count": 0,
        "mindmap_count": 0,
    }


def _build_context(
    user: User,
    enrollments: list[Enrollment],
    history: list[Enrollment],
    assessments: list[Assessment],
    attempts: list[MockExamAttempt],
    sessions: list[FlashcardSession],
    study_metadata: dict[int, dict[str, Any]],
) -> dict[str, Any]:
    now = datetime.now(timezone.utc)
    assessments_by_course = _group_assessments(assessments)
    mocks_by_course = _group_mocks(attempts)
    flashcards = _flashcard_summaries(sessions, enrollments)
    courses = _course_contexts(
        enrollments,
        assessments_by_course,
        mocks_by_course,
        study_metadata,
        now,
    )
    return {
        "student": {
            "first_name": user.first_name,
            "major": user.major or "Undeclared",
            "cgpa": user.cgpa,
            "study_year": user.study_year,
            "total_years": _infer_total_years(user),
            "study_progress": _study_year_label(
                user.study_year,
                _infer_total_years(user),
            ),
            "term": settings.CURRENT_TERM,
            "year": settings.CURRENT_YEAR,
        },
        "courses": courses,
        "overdue_items": _overdue_items(assessments, now),
        "flashcards": flashcards,
        "history": _history_context(history),
        "weak_signals": _weak_signals(courses, assessments_by_course),
    }


def _group_assessments(assessments: list[Assessment]) -> dict[int, list[Assessment]]:
    grouped: dict[int, list[Assessment]] = {}
    for item in assessments:
        grouped.setdefault(item.course_id, []).append(item)
    return grouped


def _group_mocks(attempts: list[MockExamAttempt]) -> dict[int, list[float]]:
    grouped: dict[int, list[float]] = {}
    for item in attempts:
        if item.score_pct is None:
            continue
        grouped.setdefault(item.mock_exam.course_id, []).append(float(item.score_pct))
    return grouped


def _flashcard_summaries(
    sessions: list[FlashcardSession],
    enrollments: list[Enrollment],
) -> list[dict[str, Any]]:
    course_map = {item.course_id: item.course_offering.course for item in enrollments}
    decks: dict[int, dict[str, Any]] = {}
    for session in sessions:
        deck = session.deck
        stats = decks.setdefault(deck.id, {"times_seen": 0, "hard_count": 0, "deck": deck})
        for card in session.session_cards:
            stats["times_seen"] += card.times_seen
            stats["hard_count"] += card.times_hard
    items: list[dict[str, Any]] = []
    for stats in decks.values():
        deck = stats["deck"]
        course = course_map.get(deck.course_id)
        if course is None or stats["times_seen"] == 0:
            continue
        items.append(
            {
                "course_id": deck.course_id,
                "course_code": _course_code(course),
                "deck_title": deck.title,
                "hard_rate": round(stats["hard_count"] / stats["times_seen"] * 100, 1),
                "times_seen": stats["times_seen"],
            }
        )
    return sorted(items, key=lambda item: item["hard_rate"], reverse=True)


def _course_contexts(
    enrollments: list[Enrollment],
    assessments_by_course: dict[int, list[Assessment]],
    mocks_by_course: dict[int, list[float]],
    study_metadata: dict[int, dict[str, Any]],
    now: datetime,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for enrollment in enrollments:
        course = enrollment.course_offering.course
        course_assessments = assessments_by_course.get(enrollment.course_id, [])
        metadata = study_metadata.get(enrollment.course_id, _empty_study_metadata())
        completed_scores = [
            pct
            for pct in (
                _safe_pct(item.score, item.max_score)
                for item in course_assessments
            )
            if pct is not None
        ]
        items.append(
            {
                "course_id": enrollment.course_id,
                "course_code": _course_code(course),
                "course_title": course.title,
                "ects": course.ects,
                "assessment_avg_pct": _avg_pct(completed_scores),
                "mock_avg_pct": _avg_pct(mocks_by_course.get(enrollment.course_id, [])),
                "overdue_count": sum(
                    1
                    for item in course_assessments
                    if not item.is_completed and item.deadline < now
                ),
                "study_metadata": {
                    "mock_exam_count": metadata["mock_exam_count"],
                    "flashcard_deck_count": metadata["flashcard_deck_count"],
                    "mindmap_count": metadata["mindmap_count"],
                },
                "route_options": _route_options(
                    enrollment.course_id,
                    course_assessments,
                    metadata,
                ),
            }
        )
    return items


def _route_options(
    course_id: int,
    assessments: list[Assessment],
    metadata: dict[str, Any],
) -> list[dict[str, str]]:
    routes: list[dict[str, str]] = []
    available_families = metadata["mock_families"]
    for item in assessments:
        assessment_type = item.assessment_type.value
        if assessment_type not in _ALLOWED_ACTION_TYPES:
            continue
        family = (assessment_type, item.assessment_number)
        if family not in available_families:
            continue
        label = f"{assessment_type.title()} {item.assessment_number}"
        routes.append(
            {
                "action_type": f"take_{assessment_type}",
                "label": label,
                "action_url": f"/study/{course_id}/{assessment_type}/{item.assessment_number}",
            }
        )
    if metadata["flashcard_deck_count"] > 0:
        routes.append(
            {
                "action_type": "start_flashcards",
                "label": "Open flashcards",
                "action_url": f"/study/{course_id}?tab=flashcards",
            }
        )
    if metadata["mindmap_count"] > 0:
        routes.append(
            {
                "action_type": "view_mindmap",
                "label": "Open mindmaps",
                "action_url": f"/study/{course_id}?tab=mindmaps",
            }
        )
    unique: dict[str, dict[str, str]] = {}
    for item in routes:
        unique[item["action_url"]] = item
    if unique:
        return list(unique.values())
    return [
        {
            "action_type": "take_mock",
            "label": "Review study tools",
            "action_url": f"/study/{course_id}",
        }
    ]


def _overdue_items(
    assessments: list[Assessment],
    now: datetime,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in assessments:
        if item.is_completed or item.deadline >= now:
            continue
        items.append(
            {
                "course_id": item.course_id,
                "course_code": _course_code(item.course_offering.course),
                "assessment_type": item.assessment_type.value,
                "assessment_number": item.assessment_number,
                "days_overdue": max(1, (now.date() - item.deadline.date()).days),
            }
        )
    return sorted(items, key=lambda item: item["days_overdue"], reverse=True)


def _history_context(history: list[Enrollment]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for item in history:
        items.append(
            {
                "course_code": _course_code(item.course_offering.course),
                "grade": item.grade,
                "grade_points": item.grade_points,
            }
        )
    return items


def _weak_signals(
    courses: list[dict[str, Any]],
    assessments_by_course: dict[int, list[Assessment]],
) -> list[str]:
    weak: list[str] = []
    for item in courses:
        if item["assessment_avg_pct"] is not None and item["assessment_avg_pct"] < _WEAK_SCORE_PCT:
            weak.append(f'{item["course_code"]} assessment avg {item["assessment_avg_pct"]}%')
        if item["mock_avg_pct"] is not None and item["mock_avg_pct"] < _WEAK_MOCK_PCT:
            weak.append(f'{item["course_code"]} mock avg {item["mock_avg_pct"]}%')
        weak.extend(_weak_assessment_types(item["course_id"], item["course_code"], assessments_by_course))
    return weak


def _weak_assessment_types(
    course_id: int,
    course_code: str,
    assessments_by_course: dict[int, list[Assessment]],
) -> list[str]:
    grouped: dict[str, list[float]] = {}
    for item in assessments_by_course.get(course_id, []):
        pct = _safe_pct(item.score, item.max_score)
        if pct is None:
            continue
        grouped.setdefault(item.assessment_type.value, []).append(pct)
    lines: list[str] = []
    for assessment_type, values in grouped.items():
        avg_pct = _avg_pct(values)
        if avg_pct is not None and avg_pct < _WEAK_SCORE_PCT:
            lines.append(f"{course_code} {assessment_type} avg {avg_pct}%")
    return lines
