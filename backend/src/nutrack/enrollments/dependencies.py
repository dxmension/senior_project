from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.enrollments.service import EnrollmentService


async def get_enrollment_service(
    session: AsyncSession = Depends(get_async_session),
) -> EnrollmentService:
    return EnrollmentService(session=session)
