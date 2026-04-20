from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.mock_exams.service import MockExamService


def get_mock_exam_service(
    session: AsyncSession = Depends(get_async_session),
) -> MockExamService:
    return MockExamService(session=session)
