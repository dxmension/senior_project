from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from nutrack.courses.models import Course
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.enrollments.service import EnrollmentService
from nutrack.semester import format_term_year
from nutrack.users.exceptions import NotFoundError
from nutrack.users.repository import UserRepository
from nutrack.users.schemas import (
    CreditsBySemester,
    EnrollmentResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
)
from nutrack.users.utils import term_year_sort_key


def course_loader():
    return joinedload(Enrollment.course).options(
        load_only(
            Course.id,
            Course.code,
            Course.level,
            Course.title,
            Course.ects,
        )
    )


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
        self,
        user_id: int,
        data: UserProfileUpdate,
    ) -> UserProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await self.user_repo.update(user, **update_data)

        return UserProfileResponse.model_validate(user)

    async def get_enrollments(self, user_id: int) -> list[EnrollmentResponse]:
        service = EnrollmentService(self.session)
        return await service.list_enrollments(user_id)

    async def get_stats(self, user_id: int) -> UserStatsResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        stmt = (
            select(Enrollment)
            .options(course_loader())
            .where(Enrollment.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        enrollments = list(result.scalars().unique().all())

        total_credits = user.total_credits_earned or 0
        completed_courses = len(
            [e for e in enrollments if e.status == EnrollmentStatus.PASSED]
        )
        semesters = {(e.term, e.year) for e in enrollments}

        credits_map: dict[tuple[str, int], int] = {}
        for enrollment in enrollments:
            key = (enrollment.term, enrollment.year)
            credits_map[key] = (
                credits_map.get(key, 0) + enrollment.course.ects
            )

        credits_by_semester = [
            CreditsBySemester(
                semester=format_term_year(term, year),
                term=term,
                year=year,
                credits=credits,
            )
            for (term, year), credits in sorted(
                credits_map.items(),
                key=lambda item: term_year_sort_key(item[0][0], item[0][1]),
            )
        ]

        return UserStatsResponse(
            total_credits=total_credits,
            completed_courses=completed_courses,
            current_gpa=user.cgpa,
            semesters_completed=len(semesters),
            credits_by_semester=credits_by_semester,
        )
