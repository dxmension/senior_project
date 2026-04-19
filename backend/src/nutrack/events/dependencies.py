from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.events.repository import CategoryRepository, EventRepository
from nutrack.events.service import EventCategoryService, EventService


def get_event_service(
    session: AsyncSession = Depends(get_async_session),
) -> EventService:
    return EventService(
        event_repo=EventRepository(session),
        category_repo=CategoryRepository(session),
    )


def get_event_category_service(
    session: AsyncSession = Depends(get_async_session),
) -> EventCategoryService:
    return EventCategoryService(CategoryRepository(session))
