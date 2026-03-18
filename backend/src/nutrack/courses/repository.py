from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.courses.models import Course, CourseOffering
from nutrack.shared.db.base_repository import BaseRepository


def _build_search_filter(pattern: str):
    combined_code = func.concat(Course.code, " ", Course.level)
    compact_code = func.concat(Course.code, Course.level)
    code_match = Course.code.ilike(pattern)
    combined_match = combined_code.ilike(pattern)
    compact_match = compact_code.ilike(pattern)
    level_match = Course.level.ilike(pattern)
    search_filter = or_(
        combined_match,
        compact_match,
        code_match,
        level_match,
        Course.title.ilike(pattern),
    )
    search_order = case(
        (combined_match, 0),
        (compact_match, 1),
        (code_match, 2),
        (level_match, 3),
        else_=4,
    )
    return search_filter, search_order


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

    async def search(
        self,
        query: str | None,
        limit: int,
        term: str,
        year: int,
    ) -> list[CourseOffering]:
        stmt = (
            select(CourseOffering)
            .join(CourseOffering.course)
            .options(joinedload(CourseOffering.course))
            .where(
                CourseOffering.term == term,
                CourseOffering.year == year,
            )
        )
        cleaned = (query or "").strip()
        if cleaned:
            pattern = f"%{cleaned}%"
            search_filter, search_order = _build_search_filter(pattern)
            stmt = stmt.where(search_filter).order_by(search_order)
        stmt = stmt.order_by(
            Course.code,
            Course.level,
            Course.title,
            CourseOffering.section,
        )
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
