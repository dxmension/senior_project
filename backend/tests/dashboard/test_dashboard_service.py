from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.assessments.models import AssessmentType
from nutrack.dashboard.service import DashboardService
from nutrack.enrollments.models import EnrollmentStatus


def _course(title: str = "Introductory Biology") -> SimpleNamespace:
    return SimpleNamespace(code="BIOL", level="101", title=title, ects=5)


def _enrollment() -> SimpleNamespace:
    return SimpleNamespace(
        course_id=4,
        term="Spring",
        year=2026,
        status=EnrollmentStatus.IN_PROGRESS,
        grade_points=None,
        course_offering=SimpleNamespace(
            term="Spring",
            year=2026,
            course=_course(),
        ),
    )


def _assessment() -> SimpleNamespace:
    return SimpleNamespace(
        id=7,
        course_id=4,
        assessment_type=AssessmentType.MIDTERM,
        assessment_number=2,
        deadline=datetime.now(timezone.utc) + timedelta(days=2),
        is_completed=False,
        course_offering=SimpleNamespace(course=_course()),
    )


@pytest.mark.asyncio
async def test_get_dashboard_uses_derived_assessment_titles() -> None:
    service = DashboardService(session=None)
    service._fetch_enrollments = AsyncMock(return_value=[_enrollment()])  # type: ignore[method-assign]
    service._fetch_assessments = AsyncMock(return_value=[_assessment()])  # type: ignore[method-assign]
    service._fetch_user = AsyncMock(  # type: ignore[method-assign]
        return_value=SimpleNamespace(cgpa=3.7, total_credits_earned=40)
    )

    result = await service.get_dashboard(1, "Spring", 2026)

    assert result.course_progress[0].deadline_dots[0].title == "Midterm 2"
    assert result.upcoming_deadlines[0].title == "Midterm 2"


@pytest.mark.asyncio
async def test_get_dashboard_keeps_all_deadline_dots_for_course() -> None:
    service = DashboardService(session=None)
    service._fetch_enrollments = AsyncMock(return_value=[_enrollment()])  # type: ignore[method-assign]
    service._fetch_user = AsyncMock(  # type: ignore[method-assign]
        return_value=SimpleNamespace(cgpa=3.7, total_credits_earned=40)
    )
    assessments = [
        SimpleNamespace(
            id=index,
            course_id=4,
            assessment_type=assessment_type,
            assessment_number=index,
            deadline=datetime.now(timezone.utc) + timedelta(days=index),
            is_completed=False,
            course_offering=SimpleNamespace(course=_course()),
        )
        for index, assessment_type in enumerate(
            [
                AssessmentType.HOMEWORK,
                AssessmentType.LAB,
                AssessmentType.PROJECT,
                AssessmentType.OTHER,
                AssessmentType.QUIZ,
            ],
            start=1,
        )
    ]
    service._fetch_assessments = AsyncMock(return_value=assessments)  # type: ignore[method-assign]

    result = await service.get_dashboard(1, "Spring", 2026)

    assert len(result.course_progress[0].deadline_dots) == 5
    assert result.course_progress[0].deadline_dots[-1].title == "Quiz 5"
