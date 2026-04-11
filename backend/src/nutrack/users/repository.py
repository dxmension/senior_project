from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import BaseRepository
from nutrack.users.models import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_google_id(self, google_id: str) -> User | None:
        stmt = select(User).where(User.google_id == google_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name(self, first_name: str, last_name: str) -> User | None:
        stmt = select(User).where(
            User.first_name == first_name,
            User.last_name == last_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
