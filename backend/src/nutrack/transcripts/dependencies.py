from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.redis import get_redis
from nutrack.transcripts.service import TranscriptService


async def get_transcript_service(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
) -> TranscriptService:
    return TranscriptService(session=session, redis=redis)
