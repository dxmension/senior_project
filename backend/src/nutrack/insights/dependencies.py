from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.insights.service import InsightsService
from nutrack.redis import get_redis


async def get_insights_service(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
) -> InsightsService:
    return InsightsService(session=session, redis=redis)
