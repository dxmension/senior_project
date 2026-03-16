from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.courses.models import Course
from nutrack.shared.db.base_repository import BaseRepository
from nutrack.models import Enrollment


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Course)

    async def get_by_code_and_level(
        self,
        code: str,
        level: str,
    ) -> Course | None:
        stmt = select(Course).where(
            Course.code == code,
            Course.level == level,
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
        semester: str,
    ) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
            Enrollment.semester == semester,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
