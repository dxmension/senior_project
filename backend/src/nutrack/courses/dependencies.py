from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.courses.repository import CourseOfferingRepository, CourseRepository
from nutrack.courses.service import CourseScheduleService, CourseSearchService


async def get_course_schedule_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseScheduleService:
    course_repository = CourseRepository(session)
    offering_repository = CourseOfferingRepository(session)
    return CourseScheduleService(
        course_repository=course_repository,
        offering_repository=offering_repository,
    )


async def get_course_search_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseSearchService:
    repository = CourseOfferingRepository(session)
    return CourseSearchService(repository=repository)
