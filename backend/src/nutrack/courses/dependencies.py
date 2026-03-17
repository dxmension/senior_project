from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.courses.repository import CourseRepository
from nutrack.courses.service import CourseScheduleService, CourseSearchService


async def get_course_schedule_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseScheduleService:
    repository = CourseRepository(session)
    return CourseScheduleService(repository=repository)


async def get_course_search_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseSearchService:
    repository = CourseRepository(session)
    return CourseSearchService(repository=repository)
