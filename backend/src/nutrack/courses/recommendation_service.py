"""AI-powered course recommendation service."""
from __future__ import annotations

from openai import AsyncOpenAI
from pydantic import BaseModel

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
from nutrack.courses.service import CourseEligibilityService
from nutrack.users.audit import compute_audit
from nutrack.users.models import User

_NEXT_TERM: dict[str, str] = {"Spring": "Fall", "Summer": "Fall", "Fall": "Spring"}


def _next_semester(current_term: str, current_year: int) -> tuple[str, int]:
    next_t = _NEXT_TERM.get(current_term, "Fall")
    next_y = current_year + 1 if current_term == "Fall" else current_year
    return next_t, next_y


class _OpenAIRec(BaseModel):
    course_id: int
    reason: str


class _OpenAIResponse(BaseModel):
    recommendations: list[_OpenAIRec]


class CourseRecommendationService:
    def __init__(
        self,
        course_repository: CourseRepository,
        offering_repository: CourseOfferingRepository,
        gpa_stats_repository: CourseGpaStatsRepository,
        eligibility_service: CourseEligibilityService,
    ) -> None:
        self._course_repo = course_repository
        self._offering_repo = offering_repository
        self._gpa_stats_repo = gpa_stats_repository
        self._eligibility = eligibility_service
        self._openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def get_recommendations(self, user: User) -> RecommendationsResponse:
        next_term, next_year = _next_semester(
            settings.CURRENT_TERM, settings.CURRENT_YEAR
        )

        # 1. User's full course history
        history = await self._course_repo.get_user_course_history(user.id)
        taken_catalog_ids: set[int] = {r["id"] for r in history}
        taken_codes: set[str] = {f"{r['code']} {r['level']}" for r in history}
        audit_input = [(f"{r['code']} {r['level']}", r["status"]) for r in history]

        # 2. Degree audit to find gaps
        audit = None
        if user.major:
            audit = compute_audit(
                user.major, audit_input, user.total_credits_earned or 0
            )

        # 3. All offerings for next term (up to 200)
        all_offerings = await self._offering_repo.list_by_term(
            next_term, next_year, limit=200
        )

        # 4. Group by catalog course_id, exclude already-taken courses
        course_offerings: dict[int, list[CourseOffering]] = {}
        for off in all_offerings:
            if off.course_id not in taken_catalog_ids:
                course_offerings.setdefault(off.course_id, []).append(off)

        if not course_offerings:
            return RecommendationsResponse(
                recommendations=[], term=next_term, year=next_year
            )

        # 5. Eligibility check — use first offering per catalog course
        eligible_catalog_ids: list[int] = []
        for catalog_id, offs in course_offerings.items():
            elig = await self._eligibility.check_eligibility(
                offs[0].id, user.id, user.kazakh_level
            )
            if elig.can_register:
                eligible_catalog_ids.append(catalog_id)

        if not eligible_catalog_ids:
            return RecommendationsResponse(
                recommendations=[], term=next_term, year=next_year
            )

        # 6. GPA stats for eligible courses
        gpa_map = await self._gpa_stats_repo.get_avg_gpa_by_course_ids(
            eligible_catalog_ids
        )

        # 7. Sort: priority match first, then highest avg_gpa; cap at 50 for prompt
        def _priority_match(course: Course) -> bool:
            if not user.major:
                return False
            m = user.major.lower()
            return any(
                p and m in p.lower()
                for p in [
                    course.priority_1,
                    course.priority_2,
                    course.priority_3,
                    course.priority_4,
                ]
            )

        sorted_eligible = sorted(
            eligible_catalog_ids,
            key=lambda cid: (
                not _priority_match(course_offerings[cid][0].course),
                -(gpa_map.get(cid) or 0),
            ),
        )[:50]

        # 8. Build degree gap summary for prompt
        gap_lines: list[str] = []
        if audit and audit.supported:
            for cat in audit.categories:
                for req in cat.requirements:
                    if not req.satisfied:
                        gap_lines.append(
                            f"  - {cat.name} / {req.name}: "
                            f"need {req.missing_count} more course(s)"
                        )

        # 9. Call OpenAI for top-5 ranked recommendations
        openai_recs = await self._rank_with_openai(
            user, taken_codes, gap_lines, sorted_eligible, course_offerings,
            gpa_map, _priority_match
        )

        # 10. Build final response preserving OpenAI ordering
        result: list[RecommendedCourseItem] = []
        for rec in openai_recs:
            cid = rec.course_id
            if cid not in course_offerings:
                continue
            offs = course_offerings[cid]
            c = offs[0].course
            result.append(
                RecommendedCourseItem(
                    course_id=cid,
                    offering_ids=[o.id for o in offs],
                    code=c.code,
                    level=c.level,
                    title=c.title,
                    ects=c.ects,
                    description=c.description,
                    department=c.department,
                    avg_gpa=gpa_map.get(cid),
                    priority_match=_priority_match(c),
                    reason=rec.reason,
                    offerings=[
                        RecommendedOfferingSummary(
                            section=o.section,
                            faculty=o.faculty,
                            meeting_time=o.meeting_time,
                            days=o.days,
                            room=o.room,
                            enrolled=o.enrolled,
                            capacity=o.capacity,
                        )
                        for o in offs
                    ],
                )
            )

        return RecommendationsResponse(
            recommendations=result, term=next_term, year=next_year
        )

    async def _rank_with_openai(
        self,
        user: User,
        taken_codes: set[str],
        gap_lines: list[str],
        sorted_eligible: list[int],
        course_offerings: dict[int, list[CourseOffering]],
        gpa_map: dict[int, float | None],
        priority_fn,
    ) -> list[_OpenAIRec]:
        taken_str = ", ".join(sorted(taken_codes)) or "None"
        gap_str = "\n".join(gap_lines) or "  (no audit data available)"

        course_lines: list[str] = []
        for cid in sorted_eligible:
            offs = course_offerings[cid]
            c = offs[0].course
            sched_parts = [
                f"{o.section or 'N/A'} {o.meeting_time or ''} ({o.faculty or 'TBA'})"
                for o in offs
            ]
            sched = "; ".join(sched_parts)
            prio = "MAJOR PRIORITY" if priority_fn(c) else ""
            gpa_str = f"{gpa_map[cid]:.2f}" if gpa_map.get(cid) else "N/A"
            course_lines.append(
                f"ID={cid}: {c.code} {c.level} {c.title} | "
                f"ECTS={c.ects} | avg_gpa={gpa_str} | {prio} | {sched}"
            )

        prompt = (
            f"Student profile:\n"
            f"- Major: {user.major or 'Undeclared'}\n"
            f"- Cumulative GPA: {user.cgpa or 'N/A'}\n"
            f"- Study Year: {user.study_year or 'N/A'}\n"
            f"- Credits Earned: {user.total_credits_earned or 0}\n\n"
            f"Completed/in-progress courses:\n{taken_str}\n\n"
            f"Degree audit gaps (unfulfilled requirements):\n{gap_str}\n\n"
            f"Available eligible courses for next semester:\n"
            + "\n".join(course_lines)
            + "\n\nRecommend exactly 5 courses from the list above. "
            "Prioritize: degree completion gaps > major priority access > "
            "good avg GPA > balanced workload. "
            'Return JSON: {"recommendations": [{"course_id": <int>, "reason": "<1-2 sentence reason>"}, ...]}'
        )

        response = await self._openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an academic advisor. Respond only with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            max_tokens=800,
            temperature=0.3,
        )

        raw = response.choices[0].message.content or "{}"
        try:
            parsed = _OpenAIResponse.model_validate_json(raw)
            return parsed.recommendations[:5]
        except Exception:
            return []
