from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.assessments.repository import AssessmentRepository
from nutrack.calendar.service import CalendarService
from nutrack.database import get_async_session
from nutrack.enrollments.repository import EnrollmentRepository
from nutrack.events.repository import CategoryRepository, EventRepository
from nutrack.events.service import EventService


def get_calendar_service(
    session: AsyncSession = Depends(get_async_session),
) -> CalendarService:
    event_service = EventService(
        event_repo=EventRepository(session),
        category_repo=CategoryRepository(session),
    )
    return CalendarService(
        event_service=event_service,
        assessment_repo=AssessmentRepository(session),
        enrollment_repo=EnrollmentRepository(session),
    )
