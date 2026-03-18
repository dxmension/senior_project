from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.courses.repository import CourseOfferingRepository
from nutrack.enrollments.exceptions import (
    EnrollmentConflictError,
    EnrollmentNotFoundError,
)
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.enrollments.repository import EnrollmentRepository
from nutrack.enrollments.schemas import EnrollmentItemResponse
from nutrack.semester import term_year_desc_sort_key
from nutrack.users.exceptions import NotFoundError


def format_course_code(code: str, level: str) -> str:
    if any(char.isdigit() for char in code):
        return code
    if not level or level == "0":
        return code
    return f"{code} {level.strip()}"


def build_enrollment_response(
    enrollment: Enrollment,
) -> EnrollmentItemResponse:
    offering = enrollment.course_offering
    course = offering.course
    return EnrollmentItemResponse(
        user_id=enrollment.user_id,
        course_id=enrollment.course_id,
        course_code=format_course_code(
            course.code,
            course.level,
        ),
        section=offering.section,
        course_title=course.title,
        ects=course.ects,
        grade=enrollment.grade,
        grade_points=enrollment.grade_points,
        term=enrollment.term,
        year=enrollment.year,
        status=enrollment.status.value,
        meeting_time=offering.meeting_time,
        room=offering.room,
    )


class EnrollmentService:
    def __init__(self, session: AsyncSession) -> None:
        self.course_offering_repo = CourseOfferingRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)

    async def list_enrollments(
        self,
        user_id: int,
        status: EnrollmentStatus | None = None,
    ) -> list[EnrollmentItemResponse]:
        enrollments = await self.enrollment_repo.list_by_user(user_id, status)
        ordered = sorted(
            enrollments,
            key=lambda item: term_year_desc_sort_key(item.term, item.year),
        )
        return [build_enrollment_response(item) for item in ordered]

    async def create_manual_enrollment(
        self,
        user_id: int,
        course_id: int,
    ) -> EnrollmentItemResponse:
        offering = await self.course_offering_repo.get_by_id(course_id)
        if not offering:
            raise NotFoundError("Course")
        existing = await self.enrollment_repo.get_by_identity(
            user_id,
            course_id,
            offering.term,
            offering.year,
        )
        if existing:
            raise EnrollmentConflictError()
        enrollment = await self._create(
            user_id,
            course_id,
            offering.term,
            offering.year,
        )
        return build_enrollment_response(enrollment)

    async def delete_enrollment(
        self,
        user_id: int,
        course_id: int,
        term: str,
        year: int,
    ) -> None:
        enrollment = await self.enrollment_repo.get_by_identity(
            user_id,
            course_id,
            term,
            year,
        )
        if not enrollment:
            raise EnrollmentNotFoundError()
        await self.enrollment_repo.delete(enrollment)

    async def _create(
        self,
        user_id: int,
        course_id: int,
        term: str,
        year: int,
    ) -> Enrollment:
        try:
            enrollment = await self.enrollment_repo.create(
                user_id=user_id,
                course_id=course_id,
                term=term,
                year=year,
                grade=None,
                grade_points=None,
                status=EnrollmentStatus.IN_PROGRESS,
            )
        except IntegrityError as exc:
            raise EnrollmentConflictError() from exc
        return await self._load(user_id, course_id, term, year, enrollment)

    async def _load(
        self,
        user_id: int,
        course_id: int,
        term: str,
        year: int,
        enrollment: Enrollment,
    ) -> Enrollment:
        loaded = await self.enrollment_repo.get_by_identity(
            user_id,
            course_id,
            term,
            year,
        )
        return loaded or enrollment
