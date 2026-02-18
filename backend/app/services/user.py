from sqlalchemy import select, func, distinct, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.exceptions import NotFoundError
from app.models.course import Course
from app.models.enrollment import Enrollment, EnrollmentStatus
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.user import (
    EnrollmentResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
    CreditsBySemester,
)

GRADE_POINTS_MAP = {
    "A": 4.0, "A-": 3.67,
    "B+": 3.33, "B": 3.0, "B-": 2.67,
    "C+": 2.33, "C": 2.0, "C-": 1.67,
    "D+": 1.33, "D": 1.0, "D-": 0.67,
    "F": 0.0,
}


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_profile(self, user_id: int) -> UserProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        return UserProfileResponse.model_validate(user)

    async def update_profile(self, user_id: int, data: UserProfileUpdate) -> UserProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await self.user_repo.update(user, **update_data)

        return UserProfileResponse.model_validate(user)

    async def get_enrollments(self, user_id: int) -> list[EnrollmentResponse]:
        stmt = (
            select(Enrollment)
            .options(joinedload(Enrollment.course))
            .where(Enrollment.user_id == user_id)
            .order_by(Enrollment.term.desc(), Enrollment.semester)
        )
        result = await self.session.execute(stmt)
        enrollments = result.scalars().unique().all()

        return [
            EnrollmentResponse(
                id=e.id,
                course_code=e.course.code,
                course_title=e.course.title,
                ects=e.course.ects,
                grade=e.grade,
                grade_points=e.grade_points,
                semester=e.semester,
                term=e.term,
                status=e.status.value,
            )
            for e in enrollments
        ]

    async def get_stats(self, user_id: int) -> UserStatsResponse:
        stmt = (
            select(Enrollment)
            .options(joinedload(Enrollment.course))
            .where(
                Enrollment.user_id == user_id,
                Enrollment.status == EnrollmentStatus.PASSED,
            )
        )
        result = await self.session.execute(stmt)
        enrollments = list(result.scalars().unique().all())

        total_credits = 0
        weighted_sum = 0.0
        semesters = set()
        credits_map: dict[tuple[str, int], int] = {}

        for e in enrollments:
            ects = e.course.ects
            total_credits += ects

            gp = e.grade_points if e.grade_points is not None else GRADE_POINTS_MAP.get(e.grade, 0.0)
            weighted_sum += gp * ects

            key = (e.semester, e.term)
            semesters.add(key)
            credits_map[key] = credits_map.get(key, 0) + ects

        current_gpa = round(weighted_sum / total_credits, 2) if total_credits > 0 else None

        credits_by_semester = [
            CreditsBySemester(semester=sem, term=term, credits=creds)
            for (sem, term), creds in sorted(credits_map.items(), key=lambda x: (x[0][1], x[0][0]))
        ]

        return UserStatsResponse(
            total_credits=total_credits,
            completed_courses=len(enrollments),
            current_gpa=current_gpa,
            semesters_completed=len(semesters),
            credits_by_semester=credits_by_semester,
        )
