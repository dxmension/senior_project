from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.courses.models import Course
from nutrack.enrollments.models import Enrollment
from nutrack.shared.db.base_repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Course)

    async def get_by_code_and_level(
        self,
        code: str,
        level: str,
        term: str,
        year: int,
    ) -> Course | None:
        # Transcript rows do not include section, so prefer a non-section
        # course if present and otherwise fall back to the first section.
        stmt = (
            select(Course)
            .where(
                Course.code == code,
                Course.level == level,
                Course.term == term,
                Course.year == year,
            )
            .order_by(
                case((Course.section.is_(None), 0), else_=1),
                Course.id,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        code: str,
        level: str,
        term: str,
        year: int,
        defaults: dict,
    ) -> Course:
        course = await self.get_by_code_and_level(code, level, term, year)
        if course:
            return course
        return await self.create(
            code=code,
            level=level,
            term=term,
            year=year,
            **defaults,
        )


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Enrollment)

    async def get_by_user_id(self, user_id: int) -> list[Enrollment]:
        stmt = select(Enrollment).where(Enrollment.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_course(
        self,
        user_id: int,
        course_id: int,
        term: str,
        year: int,
    ) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
            Enrollment.term == term,
            Enrollment.year == year,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
