from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.auth.service import AuthService
from nutrack.database import get_async_session
from nutrack.redis import get_redis


async def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(session=session, redis=redis)
