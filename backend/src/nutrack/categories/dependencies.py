from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.categories.repository import CategoryRepository
from nutrack.categories.service import CategoryService
from nutrack.database import get_async_session


def get_category_service(
    session: AsyncSession = Depends(get_async_session),
) -> CategoryService:
    return CategoryService(CategoryRepository(session))
