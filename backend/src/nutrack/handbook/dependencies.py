from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.handbook.service import HandbookService


async def get_handbook_service(
    session: AsyncSession = Depends(get_async_session),
) -> HandbookService:
    return HandbookService(session)
