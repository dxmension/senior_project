"""Audit-driven course recommendation service."""
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.exc import ProgrammingError

from nutrack.config import settings
from nutrack.courses.models import Course, CourseOffering
from nutrack.courses.repository import (
    CourseGpaStatsRepository,
    CourseOfferingRepository,
    CourseRepository,
)
from nutrack.courses.schemas import (
    RecommendedCourseItem,
    RecommendedOfferingSummary,
    RecommendationsResponse,
)
from nutrack.courses.service import CourseEligibilityService, _get_user_priority
from nutrack.handbook.service import HandbookService
from nutrack.users.audit import RequirementResult, compute_audit
from nutrack.users.models import User


@dataclass
class _MissingRequirement:
    category_name: str
    requirement: RequirementResult
    slots_needed: int


def _is_missing_handbook_table(error: ProgrammingError) -> bool:
    return 'relation "handbook_plans" does not exist' in str(error)


def _norm(value: str) -> str:
    return value.strip().upper()


def _level_sort_value(level: str) -> int:
    digits = "".join(ch for ch in level if ch.isdigit())
    return int(digits) if digits else 9_999


def _is_kazakh_core_requirement(requirement: RequirementResult) -> bool:
    return requirement.name.lower() == "kazakh language" and requirement.patterns == ["KAZ"]


def _kazakh_preference(course: Course, requirement: RequirementResult) -> int:
    if not _is_kazakh_core_requirement(requirement) or course.code != "KAZ":
        return 0
    level = _level_sort_value(course.level)
    if 300 <= level < 400:
        return 3
    if 200 <= level < 300:
        return 2
    if 100 <= level < 200:
        return 1
    return 0


def _matches_pattern(course_code: str, pattern: str) -> bool:
    normalized_pattern = _norm(pattern)
    if normalized_pattern == "*":
        return True
    normalized_code = _norm(course_code)
    if normalized_code == normalized_pattern:
        return True
    if not normalized_code.startswith(normalized_pattern):
        return False
    rest = normalized_code[len(normalized_pattern):]
    return not rest or rest[0] in " 0123456789"


def _match_strength(course: Course, patterns: list[str]) -> int:
    course_code = f"{course.code} {course.level}"
    exact = any(_norm(course_code) == _norm(pattern) for pattern in patterns)
    if exact:
        return 2
    prefix = any(_matches_pattern(course_code, pattern) for pattern in patterns)
    return 1 if prefix else 0


def _requirement_priority(item: _MissingRequirement) -> tuple[int, int, str]:
    elective = 1 if item.requirement.patterns == ["*"] else 0
    broad = 1 if any(" " not in pattern for pattern in item.requirement.patterns) else 0
    return elective, broad, item.category_name


def _build_reason(
    course: Course,
    category_name: str,
    requirement: RequirementResult,
) -> str:
    course_code = f"{course.code} {course.level}"
    return (
        f"{course_code} helps fulfill {category_name} / {requirement.name}."
    )


def _suggestion_limit(requirement: RequirementResult, slots_needed: int) -> int:
    if _is_kazakh_core_requirement(requirement):
        return max(3, slots_needed)
    broad_requirement = any(" " not in pattern for pattern in requirement.patterns)
    elective_like = "elective" in requirement.name.lower() or len(requirement.patterns) > 1
    if broad_requirement or elective_like:
        return max(3, slots_needed)
    return slots_needed


class CourseRecommendationService:
    def __init__(
        self,
        course_repository: CourseRepository,
        offering_repository: CourseOfferingRepository,
        gpa_stats_repository: CourseGpaStatsRepository,
        eligibility_service: CourseEligibilityService,
        handbook_service: HandbookService | None = None,
    ) -> None:
        self._course_repo = course_repository
        self._offering_repo = offering_repository
        self._gpa_stats_repo = gpa_stats_repository
        self._eligibility = eligibility_service
        self._handbook = handbook_service

    async def get_recommendations(self, user: User) -> RecommendationsResponse:
        term, year = settings.CURRENT_TERM, settings.CURRENT_YEAR
        history = await self._course_repo.get_user_course_history(user.id)
        audit = await self._build_audit(user, history)
        offerings = await self._offering_repo.list_by_term(term, year, limit=None)
        course_offerings = self._group_offerings(history, offerings)
        recommendations = await self._select_courses(user, audit, course_offerings)
        return RecommendationsResponse(
            recommendations=recommendations,
            term=term,
            year=year,
        )

    async def _build_audit(self, user: User, history: list[dict]):
        audit_input = [(f"{row['code']} {row['level']}", row["status"]) for row in history]
        handbook_plans = await self._load_handbook_plans(user)
        return compute_audit(
            user.major or "",
            audit_input,
            user.total_credits_earned or 0,
            handbook_plans,
            kazakh_level=user.kazakh_level,
        )

    async def _load_handbook_plans(self, user: User):
        if not self._handbook or not user.study_year:
            return None
        enrollment_year = settings.CURRENT_YEAR - user.study_year
        try:
            return await self._handbook.get_plans_for_year(enrollment_year)
        except ProgrammingError as exc:
            if _is_missing_handbook_table(exc):
                return None
            raise

    def _group_offerings(
        self,
        history: list[dict],
        offerings: list[CourseOffering],
    ) -> dict[int, list[CourseOffering]]:
        taken_ids = {row["id"] for row in history}
        grouped: dict[int, list[CourseOffering]] = {}
        for offering in offerings:
            if offering.course_id in taken_ids:
                continue
            grouped.setdefault(offering.course_id, []).append(offering)
        return grouped

    async def _select_courses(
        self,
        user: User,
        audit,
        course_offerings: dict[int, list[CourseOffering]],
    ) -> list[RecommendedCourseItem]:
        if not audit.supported or not course_offerings:
            return []
        eligible_ids = await self._eligible_ids(user, course_offerings)
        gpa_map = await self._gpa_stats_repo.get_avg_gpa_by_course_ids(eligible_ids)
        missing = self._missing_requirements(audit)
        return self._build_items(user, missing, course_offerings, eligible_ids, gpa_map)

    async def _eligible_ids(
        self,
        user: User,
        course_offerings: dict[int, list[CourseOffering]],
    ) -> list[int]:
        eligible_ids: list[int] = []
        for catalog_id, offerings in course_offerings.items():
            result = await self._eligibility.check_eligibility(
                offerings[0].course_id,
                user.id,
                user.kazakh_level,
            )
            if result.can_register:
                eligible_ids.append(catalog_id)
        return eligible_ids

    def _missing_requirements(self, audit) -> list[_MissingRequirement]:
        items: list[_MissingRequirement] = []
        for category in audit.categories:
            for requirement in category.requirements:
                slots = requirement.required_count - requirement.completed_count
                slots -= requirement.in_progress_count
                if slots > 0:
                    items.append(
                        _MissingRequirement(
                            category_name=category.name,
                            requirement=requirement,
                            slots_needed=slots,
                        )
                    )
        return sorted(items, key=_requirement_priority)

    def _build_items(
        self,
        user: User,
        missing: list[_MissingRequirement],
        course_offerings: dict[int, list[CourseOffering]],
        eligible_ids: list[int],
        gpa_map: dict[int, float | None],
    ) -> list[RecommendedCourseItem]:
        selected: list[RecommendedCourseItem] = []
        used_ids: set[int] = set()
        total_limit = 8
        for item in missing:
            matches = self._rank_matches(
                user,
                item.requirement,
                course_offerings,
                eligible_ids,
                gpa_map,
                used_ids,
            )
            per_requirement_limit = _suggestion_limit(
                item.requirement,
                item.slots_needed,
            )
            remaining_slots = total_limit - len(selected)
            if remaining_slots <= 0:
                break
            for course_id in matches[: min(per_requirement_limit, remaining_slots)]:
                selected.append(
                    self._recommendation_item(
                        item.category_name,
                        item.requirement,
                        course_offerings[course_id],
                        gpa_map,
                        user.major,
                    )
                )
                used_ids.add(course_id)
            if len(selected) >= total_limit:
                break
        return selected[:total_limit]

    def _rank_matches(
        self,
        user: User,
        requirement: RequirementResult,
        course_offerings: dict[int, list[CourseOffering]],
        eligible_ids: list[int],
        gpa_map: dict[int, float | None],
        used_ids: set[int],
    ) -> list[int]:
        scored: list[tuple[tuple, int]] = []
        broad_requirement = any(" " not in pattern for pattern in requirement.patterns)
        for course_id in eligible_ids:
            if course_id in used_ids:
                continue
            course = course_offerings[course_id][0].course
            strength = _match_strength(course, requirement.patterns)
            if not strength:
                continue
            priority = _get_user_priority(course, user.major) is not None
            kazakh_score = _kazakh_preference(course, requirement)
            level_score = -_level_sort_value(course.level) if broad_requirement else 0
            score = (
                strength,
                priority,
                kazakh_score,
                level_score,
                gpa_map.get(course_id) or 0,
                -course.id,
            )
            scored.append((score, course_id))
        scored.sort(reverse=True)
        return [course_id for _, course_id in scored]

    def _recommendation_item(
        self,
        category_name: str,
        requirement: RequirementResult,
        offerings: list[CourseOffering],
        gpa_map: dict[int, float | None],
        user_major: str | None,
    ) -> RecommendedCourseItem:
        course = offerings[0].course
        return RecommendedCourseItem(
            course_id=course.id,
            offering_ids=[offering.id for offering in offerings],
            code=course.code,
            level=course.level,
            title=course.title,
            ects=course.ects,
            description=course.description,
            department=course.department,
            avg_gpa=gpa_map.get(course.id),
            priority_match=_get_user_priority(course, user_major) is not None,
            reason=_build_reason(course, category_name, requirement),
            offerings=[
                RecommendedOfferingSummary(
                    section=offering.section,
                    faculty=offering.faculty,
                    meeting_time=offering.meeting_time,
                    days=offering.days,
                    room=offering.room,
                    enrolled=offering.enrolled,
                    capacity=offering.capacity,
                )
                for offering in offerings
            ],
        )
