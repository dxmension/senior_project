from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import BaseRepository
from nutrack.mindmaps.models import Mindmap


class MindmapRepository(BaseRepository[Mindmap]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Mindmap)

    async def list_by_course_and_user(
        self, user_id: int, course_id: int
    ) -> list[Mindmap]:
        stmt = (
            select(Mindmap)
            .where(Mindmap.user_id == user_id, Mindmap.course_id == course_id)
            .order_by(Mindmap.week, Mindmap.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, mindmap_id: int, user_id: int
    ) -> Mindmap | None:
        stmt = select(Mindmap).where(
            Mindmap.id == mindmap_id,
            Mindmap.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
