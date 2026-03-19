from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.assessments.repository import AssessmentRepository
from nutrack.assessments.service import AssessmentService
from nutrack.database import get_async_session
from nutrack.enrollments.repository import EnrollmentRepository


def get_assessment_service(
    session: AsyncSession = Depends(get_async_session),
) -> AssessmentService:
    assessment_repo = AssessmentRepository(session)
    enrollment_repo = EnrollmentRepository(session)
    return AssessmentService(assessment_repo, enrollment_repo)
