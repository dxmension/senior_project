from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from nutrack.courses.models import Course
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.shared.db.base_repository import BaseRepository


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

    def _base_query(self) -> Select[tuple[Enrollment]]:
        return select(Enrollment).options(course_loader())
