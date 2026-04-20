from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from nutrack.courses.models import Course, CourseOffering
from nutrack.database import BaseRepository
from nutrack.enrollments.models import Enrollment, EnrollmentStatus


def course_offering_loader():
    return joinedload(Enrollment.course_offering).options(
        load_only(
            CourseOffering.id,
            CourseOffering.course_id,
            CourseOffering.section,
            CourseOffering.term,
            CourseOffering.year,
            CourseOffering.days,
            CourseOffering.meeting_time,
            CourseOffering.room,
        ),
        joinedload(CourseOffering.course).load_only(
            Course.code,
            Course.level,
            Course.title,
            Course.ects,
        ),
    )


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Enrollment)

    async def list_by_user(
        self,
        user_id: int,
        status: EnrollmentStatus | None = None,
    ) -> list[Enrollment]:
        stmt = self._base_query().where(Enrollment.user_id == user_id)
        if status is not None:
            stmt = stmt.where(Enrollment.status == status)
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_identity(
        self,
        user_id: int,
        course_id: int,
        term: str,
        year: int,
    ) -> Enrollment | None:
        stmt = self._base_query().where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
            Enrollment.term == term,
            Enrollment.year == year,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def sum_active_ects(self, user_id: int, term: str, year: int) -> int:
        stmt = (
            select(func.coalesce(func.sum(Course.ects), 0))
            .join(Enrollment.course_offering)
            .join(CourseOffering.course)
            .where(
                Enrollment.user_id == user_id,
                Enrollment.term == term,
                Enrollment.year == year,
                Enrollment.status == EnrollmentStatus.IN_PROGRESS,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one() or 0

    async def list_active_offerings(
        self, user_id: int, term: str, year: int
    ) -> list[CourseOffering]:
        stmt = (
            select(CourseOffering)
            .join(Enrollment, Enrollment.course_id == CourseOffering.id)
            .where(
                Enrollment.user_id == user_id,
                Enrollment.term == term,
                Enrollment.year == year,
                Enrollment.status == EnrollmentStatus.IN_PROGRESS,
            )
            .options(joinedload(CourseOffering.course))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    def _base_query(self) -> Select[tuple[Enrollment]]:
        return select(Enrollment).options(course_offering_loader())
