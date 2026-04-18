import asyncio
import json
from datetime import datetime, timedelta, timezone
from math import floor

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.assessments.models import Assessment
from nutrack.courses.models import Course, CourseOffering
from nutrack.dashboard.exceptions import AISummaryUnavailableError
from nutrack.dashboard.schemas import (
    AISummaryResponse,
    CourseProgressItem,
    DeadlineDotItem,
    DashboardResponse,
    UpcomingDeadlineItem,
    WeeklyWorkloadItem,
    WorkloadAssessmentItem,
)
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.users.models import User


def _course_code(course: Course) -> str:
    level = (course.level or "").strip()
    return f"{course.code} {level}" if level and level != "0" else course.code


def _compute_gpa(
    enrollments: list[Enrollment],
    statuses: set[EnrollmentStatus],
    term: str | None = None,
    year: int | None = None,
) -> float | None:
    total_ects = 0
    total_points = 0.0
    for e in enrollments:
        if e.status not in statuses:
            continue
        if e.grade_points is None:
            continue
        if term is not None and e.term != term:
            continue
        if year is not None and e.year != year:
            continue
        ects = e.course_offering.course.ects
        total_ects += ects
        total_points += e.grade_points * ects
    if total_ects == 0:
        return None
    return round(total_points / total_ects, 2)


class DashboardService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _fetch_enrollments(self, user_id: int) -> list[Enrollment]:
        stmt = (
            select(Enrollment)
            .options(
                joinedload(Enrollment.course_offering).joinedload(CourseOffering.course)
            )
            .where(Enrollment.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_assessments(self, user_id: int) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .options(
                joinedload(Assessment.course_offering).joinedload(CourseOffering.course)
            )
            .where(Assessment.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_user(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_dashboard(
        self, user_id: int, current_term: str, current_year: int
    ) -> DashboardResponse:
        enrollments, assessments, user = await asyncio.gather(
            self._fetch_enrollments(user_id),
            self._fetch_assessments(user_id),
            self._fetch_user(user_id),
        )

        now = datetime.now(tz=timezone.utc)
        today = now.date()

        # GPA
        gpa_statuses = {EnrollmentStatus.PASSED, EnrollmentStatus.IN_PROGRESS}
        current_gpa = _compute_gpa(enrollments, gpa_statuses)
        if current_gpa is None and user and user.cgpa is not None:
            current_gpa = user.cgpa
        semester_gpa = _compute_gpa(
            enrollments, gpa_statuses, current_term, current_year
        )

        # Credits
        active_enrollments = [
            e
            for e in enrollments
            if e.status == EnrollmentStatus.IN_PROGRESS
            and e.term == current_term
            and e.year == current_year
        ]
        total_credits_enrolled = sum(
            e.course_offering.course.ects for e in active_enrollments
        )
        total_credits_earned = (user.total_credits_earned or 0) if user else 0

        # Course counts
        active_courses_count = len(active_enrollments)
        completed_courses_count = sum(
            1 for e in enrollments if e.status == EnrollmentStatus.PASSED
        )

        # Assessment counts
        upcoming_deadlines_count = sum(
            1
            for a in assessments
            if not a.is_completed and now <= a.deadline < now + timedelta(days=7)
        )
        overdue_count = sum(
            1 for a in assessments if not a.is_completed and a.deadline < now
        )

        # Course progress (IN_PROGRESS this term only)
        assessment_by_course: dict[int, list[Assessment]] = {}
        for a in assessments:
            assessment_by_course.setdefault(a.course_id, []).append(a)

        course_progress = []
        for e in active_enrollments:
            course = e.course_offering.course
            offering = e.course_offering
            course_assessments = assessment_by_course.get(e.course_id, [])
            total = len(course_assessments)
            completed = sum(1 for a in course_assessments if a.is_completed)
            progress_pct = (completed / total * 100) if total > 0 else 0.0
            upcoming_dl = min(
                (
                    a.deadline
                    for a in course_assessments
                    if not a.is_completed and a.deadline >= now
                ),
                default=None,
            )
            dots_sorted = sorted(course_assessments, key=lambda a: a.deadline)[:4]
            deadline_dots = [
                DeadlineDotItem(
                    assessment_id=a.id,
                    title=a.title,
                    assessment_type=a.assessment_type.value,
                    deadline=a.deadline,
                    is_completed=a.is_completed,
                )
                for a in dots_sorted
            ]
            course_progress.append(
                CourseProgressItem(
                    course_id=e.course_id,
                    course_code=_course_code(course),
                    course_title=course.title,
                    term=offering.term,
                    year=offering.year,
                    ects=course.ects,
                    total_assessments=total,
                    completed_assessments=completed,
                    progress_pct=round(progress_pct, 1),
                    upcoming_deadline=upcoming_dl,
                    deadline_dots=deadline_dots,
                )
            )

        # Upcoming deadlines (next 10 non-completed, sorted ASC)
        pending = sorted(
            (a for a in assessments if not a.is_completed and a.deadline >= now),
            key=lambda a: a.deadline,
        )[:10]
        upcoming_deadlines = [
            UpcomingDeadlineItem(
                assessment_id=a.id,
                title=a.title,
                assessment_type=a.assessment_type.value,
                deadline=a.deadline,
                course_code=_course_code(a.course_offering.course),
                course_title=a.course_offering.course.title,
                is_completed=a.is_completed,
                days_until=max(
                    0, floor((a.deadline - now).total_seconds() / 86400)
                ),
            )
            for a in pending
        ]

        # Weekly workload (next 4 weeks from Monday of current week)
        monday = today - timedelta(days=today.weekday())
        weekly_workload = []
        for i in range(4):
            week_start = monday + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            bucket = sorted(
                [
                    a
                    for a in assessments
                    if week_start <= a.deadline.date() <= week_end
                ],
                key=lambda a: a.deadline,
            )
            weekly_workload.append(
                WeeklyWorkloadItem(
                    week_start=week_start,
                    week_label=(
                        f"{week_start.strftime('%b %d')} – {week_end.strftime('%b %d')}"
                    ),
                    assessment_count=len(bucket),
                    assessments=[
                        WorkloadAssessmentItem(
                            assessment_id=a.id,
                            title=a.title,
                            assessment_type=a.assessment_type.value,
                            deadline=a.deadline,
                            course_code=_course_code(a.course_offering.course),
                            is_completed=a.is_completed,
                        )
                        for a in bucket
                    ],
                )
            )

        return DashboardResponse(
            current_gpa=current_gpa,
            semester_gpa=semester_gpa,
            total_credits_earned=total_credits_earned,
            total_credits_enrolled=total_credits_enrolled,
            active_courses_count=active_courses_count,
            completed_courses_count=completed_courses_count,
            upcoming_deadlines_count=upcoming_deadlines_count,
            overdue_count=overdue_count,
            course_progress=course_progress,
            upcoming_deadlines=upcoming_deadlines,
            weekly_workload=weekly_workload,
        )

    async def get_ai_summary(
        self, user_id: int, current_term: str, current_year: int
    ) -> AISummaryResponse:
        from nutrack.config import settings

        if not settings.OPENAI_API_KEY:
            raise AISummaryUnavailableError("No API key configured")

        enrollments, assessments, user = await asyncio.gather(
            self._fetch_enrollments(user_id),
            self._fetch_assessments(user_id),
            self._fetch_user(user_id),
        )

        now = datetime.now(tz=timezone.utc)
        gpa_statuses = {EnrollmentStatus.PASSED, EnrollmentStatus.IN_PROGRESS}
        current_gpa = _compute_gpa(enrollments, gpa_statuses)
        if current_gpa is None and user and user.cgpa is not None:
            current_gpa = user.cgpa

        active_enrollments = [
            e
            for e in enrollments
            if e.status == EnrollmentStatus.IN_PROGRESS
            and e.term == current_term
            and e.year == current_year
        ]

        assessment_by_course: dict[int, list[Assessment]] = {}
        for a in assessments:
            assessment_by_course.setdefault(a.course_id, []).append(a)

        active_courses_ctx = [
            {
                "code": _course_code(e.course_offering.course),
                "title": e.course_offering.course.title,
                "progress_pct": round(
                    (
                        sum(
                            1
                            for a in assessment_by_course.get(e.course_id, [])
                            if a.is_completed
                        )
                        / len(assessment_by_course[e.course_id])
                        * 100
                    )
                    if assessment_by_course.get(e.course_id)
                    else 0.0,
                    1,
                ),
                "ects": e.course_offering.course.ects,
            }
            for e in active_enrollments
        ]

        pending = sorted(
            (a for a in assessments if not a.is_completed and a.deadline >= now),
            key=lambda a: a.deadline,
        )[:5]
        upcoming_ctx = [
            {
                "title": a.title,
                "type": a.assessment_type.value,
                "course": _course_code(a.course_offering.course),
                "deadline": a.deadline.isoformat(),
                "days_until": max(
                    0, floor((a.deadline - now).total_seconds() / 86400)
                ),
            }
            for a in pending
        ]

        overdue_count = sum(
            1 for a in assessments if not a.is_completed and a.deadline < now
        )
        active_course_ids = {e.course_id for e in active_enrollments}
        completed_this_term = sum(
            1 for a in assessments if a.is_completed and a.course_id in active_course_ids
        )

        system_prompt = (
            "You are an academic advisor assistant for a university student.\n"
            "Given a snapshot of the student's academic performance, generate a concise JSON response.\n"
            "Be encouraging, specific, and actionable. Keep the tone warm and motivational.\n"
            "Respond ONLY with valid JSON in this exact structure:\n"
            "{\n"
            '  "summary": "<3-5 sentence paragraph about their current academic standing>",\n'
            '  "recommendations": ["<action item 1>", "<action item 2>", "<action item 3>"],\n'
            '  "motivation": "<1-2 sentence motivational closer>"\n'
            "}"
        )
        user_prompt = (
            f"Student academic snapshot:\n"
            f"- Semester: {current_term} {current_year}\n"
            f"- Current GPA: {current_gpa}\n"
            f"- Active courses ({len(active_courses_ctx)}): {json.dumps(active_courses_ctx)}\n"
            f"- Upcoming deadlines (next 5): {json.dumps(upcoming_ctx)}\n"
            f"- Overdue tasks: {overdue_count}\n"
            f"- Completed assessments this semester: {completed_this_term}\n\n"
            f"Generate the academic summary and recommendations."
        )

        try:
            import openai

            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0.7,
                max_tokens=500,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
            )
            raw = response.choices[0].message.content
            data = json.loads(raw)
        except AISummaryUnavailableError:
            raise
        except Exception as exc:
            raise AISummaryUnavailableError(str(exc)) from exc

        return AISummaryResponse(
            summary=data["summary"],
            recommendations=data["recommendations"],
            motivation=data["motivation"],
            generated_at=datetime.now(tz=timezone.utc),
        )
