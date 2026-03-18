from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.courses.models import Course, CourseOffering
from nutrack.enrollments.models import Enrollment
from nutrack.shared.db.base_repository import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Course)

    async def get_by_code_and_level(
        self,
        code: str,
        level: str,
    ) -> Course | None:
        stmt = (
            select(Course)
            .where(Course.code == code, Course.level == level)
            .order_by(Course.id)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        code: str,
        level: str,
        defaults: dict,
    ) -> Course:
        course = await self.get_by_code_and_level(code, level)
        if course:
            return course
        return await self.create(code=code, level=level, **defaults)


class CourseOfferingRepository(BaseRepository[CourseOffering]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseOffering)

    async def get_by_identity(
        self,
        course_id: int,
        term: str,
        year: int,
        section: str | None,
    ) -> CourseOffering | None:
        stmt = select(CourseOffering).where(
            CourseOffering.course_id == course_id,
            CourseOffering.term == term,
            CourseOffering.year == year,
        )
        if section is None:
            stmt = stmt.where(CourseOffering.section.is_(None))
        else:
            stmt = stmt.where(CourseOffering.section == section)
        stmt = stmt.order_by(CourseOffering.id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        course_id: int,
        term: str,
        year: int,
        section: str | None,
        defaults: dict,
    ) -> CourseOffering:
        offering = await self.get_by_identity(course_id, term, year, section)
        if offering:
            return offering
        return await self.create(
            course_id=course_id,
            term=term,
            year=year,
            section=section,
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
