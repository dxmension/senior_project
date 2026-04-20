from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.courses.repository import (
    CourseGpaStatsRepository,
    CourseOfferingRepository,
    CourseRepository,
    CourseReviewRepository,
)
from nutrack.courses.service import (
    CourseCatalogService,
    CourseEligibilityService,
    CourseGpaStatsService,
    CourseRequirementsService,
    CourseReviewService,
    CourseScheduleService,
    CourseSearchService,
    CourseStatsService,
)


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


async def get_course_catalog_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseCatalogService:
    return CourseCatalogService(
        course_repository=CourseRepository(session),
        gpa_stats_repository=CourseGpaStatsRepository(session),
        offering_repository=CourseOfferingRepository(session),
        review_repository=CourseReviewRepository(session),
    )


async def get_course_stats_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseStatsService:
    return CourseStatsService(course_repository=CourseRepository(session))


async def get_course_gpa_stats_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseGpaStatsService:
    return CourseGpaStatsService(
        course_repository=CourseRepository(session),
        gpa_stats_repository=CourseGpaStatsRepository(session),
    )


async def get_course_requirements_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseRequirementsService:
    return CourseRequirementsService(course_repository=CourseRepository(session))


async def get_course_eligibility_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseEligibilityService:
    return CourseEligibilityService(course_repository=CourseRepository(session))


async def get_course_review_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseReviewService:
    return CourseReviewService(
        course_repository=CourseRepository(session),
        review_repository=CourseReviewRepository(session),
    )


async def get_recommendation_service(
    session: AsyncSession = Depends(get_async_session),
):
    from nutrack.courses.recommendation_service import CourseRecommendationService

    return CourseRecommendationService(
        course_repository=CourseRepository(session),
        offering_repository=CourseOfferingRepository(session),
        gpa_stats_repository=CourseGpaStatsRepository(session),
        eligibility_service=CourseEligibilityService(
            course_repository=CourseRepository(session)
        ),
    )
