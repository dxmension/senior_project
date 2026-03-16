from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.users.repository import UserRepository


class AuthUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)
