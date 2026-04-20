from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import BaseRepository
from nutrack.study_helper.models import StudyGuide, WeekOverviewCache


class WeekOverviewCacheRepository(BaseRepository[WeekOverviewCache]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, WeekOverviewCache)

    async def find_cached(
        self,
        user_id: int,
        course_id: int,
        week: int,
    ) -> WeekOverviewCache | None:
        stmt = select(WeekOverviewCache).where(
            WeekOverviewCache.user_id == user_id,
            WeekOverviewCache.course_id == course_id,
            WeekOverviewCache.week == week,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_cached_weeks(
        self,
        user_id: int,
        course_id: int,
    ) -> list[WeekOverviewCache]:
        stmt = (
            select(WeekOverviewCache)
            .where(
                WeekOverviewCache.user_id == user_id,
                WeekOverviewCache.course_id == course_id,
            )
            .order_by(WeekOverviewCache.week)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StudyGuideRepository(BaseRepository[StudyGuide]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudyGuide)

    async def find_cached(
        self,
        user_id: int,
        course_id: int,
        topic: str,
    ) -> StudyGuide | None:
        stmt = select(StudyGuide).where(
            StudyGuide.user_id == user_id,
            StudyGuide.course_id == course_id,
            StudyGuide.topic == topic,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_user_and_course(
        self,
        user_id: int,
        course_id: int,
    ) -> list[StudyGuide]:
        stmt = (
            select(StudyGuide)
            .where(
                StudyGuide.user_id == user_id,
                StudyGuide.course_id == course_id,
            )
            .order_by(StudyGuide.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self,
        guide_id: int,
        user_id: int,
    ) -> StudyGuide | None:
        stmt = select(StudyGuide).where(
            StudyGuide.id == guide_id,
            StudyGuide.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
