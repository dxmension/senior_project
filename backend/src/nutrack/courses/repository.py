from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.courses.models import Course
from nutrack.shared.db.base_repository import BaseRepository


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

    async def get_by_code_level_and_section(
        self,
        code: str,
        level: str,
        section: str | None,
    ) -> Course | None:
        stmt = select(Course).where(
            Course.code == code,
            Course.level == level,
        )
        if section is None:
            stmt = stmt.where(Course.section.is_(None))
        else:
            stmt = stmt.where(Course.section == section)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
