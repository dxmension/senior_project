from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transcript import Transcript
from app.repositories.base import BaseRepository


class TranscriptRepository(BaseRepository[Transcript]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Transcript)

    async def get_by_user_id(self, user_id: int) -> Transcript | None:
        stmt = select(Transcript).where(Transcript.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
