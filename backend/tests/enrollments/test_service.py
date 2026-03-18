from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.enrollments.exceptions import (
    EnrollmentConflictError,
    EnrollmentNotFoundError,
)
from nutrack.enrollments.models import EnrollmentStatus
from nutrack.enrollments.service import EnrollmentService
from nutrack.users.exceptions import NotFoundError


def make_enrollment(
    term: str,
    year: int,
    status: EnrollmentStatus = EnrollmentStatus.IN_PROGRESS,
):
    course = SimpleNamespace(
        code="CSCI",
        level="151",
        title="Programming",
        ects=6,
    )
    offering = SimpleNamespace(
        id=7,
        course_id=4,
        section="2",
        term=term,
        year=year,
        meeting_time="10:00-10:50",
        room="6.310",
        course=course,
    )
    return SimpleNamespace(
        user_id=1,
        course_id=7,
        term=term,
        year=year,
        grade=None,
        grade_points=None,
        status=status,
        course_offering=offering,
    )


@pytest.mark.asyncio
async def test_create_manual_enrollment_sets_defaults() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    create_mock = AsyncMock(return_value=created)
    load_mock = AsyncMock(side_effect=[None, created])

    service.course_offering_repo.get_by_id = AsyncMock(
        return_value=created.course_offering
    )
    service.enrollment_repo.get_by_identity = load_mock
    service.enrollment_repo.create = create_mock

    response = await service.create_manual_enrollment(1, 7)

    create_mock.assert_awaited_once_with(
        user_id=1,
        course_id=7,
        term="Fall",
        year=2026,
        grade=None,
        grade_points=None,
        status=EnrollmentStatus.IN_PROGRESS,
    )
    assert response.status == "in_progress"
    assert response.grade is None
    assert response.grade_points is None
    assert response.term == "Fall"
    assert response.year == 2026
    assert response.section == "2"
    assert response.meeting_time == "10:00-10:50"
    assert response.room == "6.310"


@pytest.mark.asyncio
async def test_create_manual_enrollment_rejects_duplicates() -> None:
    service = EnrollmentService(session=None)
    service.course_offering_repo.get_by_id = AsyncMock(
        return_value=SimpleNamespace(term="Fall", year=2026)
    )
    service.enrollment_repo.get_by_identity = AsyncMock(
        return_value=make_enrollment("Fall", 2026)
    )

    with pytest.raises(EnrollmentConflictError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_create_manual_enrollment_requires_existing_course() -> None:
    service = EnrollmentService(session=None)
    service.course_offering_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_delete_enrollment_removes_matching_identity() -> None:
    service = EnrollmentService(session=None)
    enrollment = make_enrollment("Fall", 2026)
    service.enrollment_repo.get_by_identity = AsyncMock(return_value=enrollment)
    service.enrollment_repo.delete = AsyncMock()

    await service.delete_enrollment(1, 7, "Fall", 2026)

    service.enrollment_repo.delete.assert_awaited_once_with(enrollment)


@pytest.mark.asyncio
async def test_delete_enrollment_raises_for_missing_row() -> None:
    service = EnrollmentService(session=None)
    service.enrollment_repo.get_by_identity = AsyncMock(return_value=None)

    with pytest.raises(EnrollmentNotFoundError):
        await service.delete_enrollment(1, 7, "Fall", 2026)


@pytest.mark.asyncio
async def test_list_enrollments_filters_and_orders_results() -> None:
    service = EnrollmentService(session=None)
    older = make_enrollment("Spring", 2026)
    newer = make_enrollment("Fall", 2026)
    service.enrollment_repo.list_by_user = AsyncMock(return_value=[older, newer])

    response = await service.list_enrollments(
        1,
        EnrollmentStatus.IN_PROGRESS,
    )

    service.enrollment_repo.list_by_user.assert_awaited_once_with(
        1,
        EnrollmentStatus.IN_PROGRESS,
    )
    assert [(item.term, item.year) for item in response] == [
        ("Fall", 2026),
        ("Spring", 2026),
    ]
