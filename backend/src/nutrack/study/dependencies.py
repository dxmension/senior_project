from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.study.service import StudyService


def get_study_service(
    session: AsyncSession = Depends(get_async_session),
) -> StudyService:
    return StudyService(session=session)
