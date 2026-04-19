from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.flashcards.service import FlashcardsService


def get_flashcards_service(
    session: AsyncSession = Depends(get_async_session),
) -> FlashcardsService:
    return FlashcardsService(session=session)
