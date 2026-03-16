from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from nutrack.courses.models import Course
from nutrack.models import Enrollment, EnrollmentStatus
from nutrack.users.exceptions import NotFoundError
from nutrack.users.repository import UserRepository
from nutrack.users.schemas import (
    CreditsBySemester,
    EnrollmentResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
)
from nutrack.users.utils import semester_desc_sort_key, semester_sort_key


def format_course_code(code: str, level: str) -> str:
    if any(char.isdigit() for char in code):
        return code
    clean_level = (level or "").strip()
    if not clean_level or clean_level == "0":
        return code
    return f"{code} {clean_level}"


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
        stmt = (
            select(Enrollment)
            .options(course_loader())
            .where(Enrollment.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        enrollments = result.scalars().unique().all()
        ordered_enrollments = sorted(
            enrollments,
            key=lambda enrollment: semester_desc_sort_key(
                enrollment.semester
            ),
        )

        return [
            EnrollmentResponse(
                id=enrollment.id,
                course_code=format_course_code(
                    enrollment.course.code,
                    enrollment.course.level,
                ),
                course_title=enrollment.course.title,
                ects=enrollment.course.ects,
                grade=enrollment.grade,
                grade_points=enrollment.grade_points,
                semester=enrollment.semester,
                status=enrollment.status.value,
            )
            for enrollment in ordered_enrollments
        ]

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
        semesters = {e.semester for e in enrollments}

        credits_map: dict[str, int] = {}
        for enrollment in enrollments:
            credits_map[enrollment.semester] = (
                credits_map.get(enrollment.semester, 0) + enrollment.course.ects
            )

        credits_by_semester = [
            CreditsBySemester(
                semester=semester,
                term=semester_sort_key(semester)[1],
                credits=credits,
            )
            for semester, credits in sorted(
                credits_map.items(),
                key=lambda item: semester_sort_key(item[0]),
            )
        ]

        return UserStatsResponse(
            total_credits=total_credits,
            completed_courses=completed_courses,
            current_gpa=user.cgpa,
            semesters_completed=len(semesters),
            credits_by_semester=credits_by_semester,
        )
