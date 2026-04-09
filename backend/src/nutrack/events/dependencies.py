from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.categories.repository import CategoryRepository
from nutrack.database import get_async_session
from nutrack.events.repository import EventRepository
from nutrack.events.service import EventService


def get_event_service(
    session: AsyncSession = Depends(get_async_session),
) -> EventService:
    return EventService(
        event_repo=EventRepository(session),
        category_repo=CategoryRepository(session),
    )
