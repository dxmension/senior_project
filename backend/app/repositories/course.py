from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course
from app.repositories.base import BaseRepository


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Course)

    async def get_by_code(self, code: str) -> Course | None:
        stmt = select(Course).where(Course.code == code)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self, code: str, defaults: dict) -> Course:
        course = await self.get_by_code(code)
        if course:
            return course
        return await self.create(code=code, **defaults)
