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
    "A": 4.0,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.0,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.0,
    "C-": 1.67,
    "D+": 1.33,
    "D": 1.0,
    "D-": 0.67,
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

    async def update_profile(
        self, user_id: int, data: UserProfileUpdate
    ) -> UserProfileResponse:
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
                status=e.status.value,
            )
            for e in enrollments
        ]

    async def get_stats(self, user_id: int) -> UserStatsResponse:
        # Get user to access their cgpa and total credits
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        
        stmt = (
            select(Enrollment)
            .options(joinedload(Enrollment.course))
            .where(Enrollment.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        enrollments = list(result.scalars().unique().all())

        total_credits = user.total_credits_earned or 0
        completed_courses = len([e for e in enrollments if e.status == EnrollmentStatus.PASSED])
        semesters = set()
        credits_map: dict[str, int] = {}

        for e in enrollments:
            semesters.add(e.semester)
            credits_map[e.semester] = credits_map.get(e.semester, 0) + e.course.ects

        credits_by_semester = [
            CreditsBySemester(semester=sem, term=0, credits=creds)
            for sem, creds in sorted(credits_map.items())
        ]

        return UserStatsResponse(
            total_credits=total_credits,
            completed_courses=completed_courses,
            current_gpa=user.cgpa,
            semesters_completed=len(semesters),
            credits_by_semester=credits_by_semester,
        )
