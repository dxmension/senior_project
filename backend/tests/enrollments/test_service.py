from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.courses.schemas import EligibilityResponse
from nutrack.enrollments.exceptions import (
    EnrollmentConflictError,
    EnrollmentCreditsExceededError,
    EnrollmentEligibilityError,
    EnrollmentNotFoundError,
    EnrollmentScheduleConflictError,
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
        id=4,
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
        days="MWF",
        meeting_time="10:00 AM - 10:50 AM",
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


def _eligible_response(course_id: int = 4) -> EligibilityResponse:
    return EligibilityResponse(
        course_id=course_id,
        can_register=True,
        prerequisites_met=True,
        corequisites_met=True,
        antirequisites_blocking=False,
    )


def _setup_create_mocks(service: EnrollmentService, offering, enrollment) -> None:
    service.course_offering_repo.get_by_id_with_course = AsyncMock(return_value=offering)
    service.eligibility_service.check_eligibility = AsyncMock(
        return_value=_eligible_response(offering.course_id)
    )
    service.enrollment_repo.sum_active_ects = AsyncMock(return_value=0)
    service.enrollment_repo.list_active_offerings = AsyncMock(return_value=[])
    service.enrollment_repo.get_by_identity = AsyncMock(side_effect=[None, enrollment])
    service.enrollment_repo.create = AsyncMock(return_value=enrollment)


@pytest.mark.asyncio
async def test_create_manual_enrollment_sets_defaults() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    _setup_create_mocks(service, created.course_offering, created)

    response = await service.create_manual_enrollment(1, 7)

    service.enrollment_repo.create.assert_awaited_once_with(
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
    assert response.catalog_course_id == 4
    assert response.section == "2"
    assert response.meeting_time == "10:00 AM - 10:50 AM"
    assert response.room == "6.310"


@pytest.mark.asyncio
async def test_create_manual_enrollment_rejects_duplicates() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    service.course_offering_repo.get_by_id_with_course = AsyncMock(
        return_value=created.course_offering
    )
    service.eligibility_service.check_eligibility = AsyncMock(
        return_value=_eligible_response()
    )
    service.enrollment_repo.sum_active_ects = AsyncMock(return_value=0)
    service.enrollment_repo.list_active_offerings = AsyncMock(return_value=[])
    service.enrollment_repo.get_by_identity = AsyncMock(return_value=created)

    with pytest.raises(EnrollmentConflictError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_create_manual_enrollment_requires_existing_course() -> None:
    service = EnrollmentService(session=None)
    service.course_offering_repo.get_by_id_with_course = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_create_manual_enrollment_blocks_ineligible() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    service.course_offering_repo.get_by_id_with_course = AsyncMock(
        return_value=created.course_offering
    )
    service.eligibility_service.check_eligibility = AsyncMock(
        return_value=EligibilityResponse(
            course_id=4,
            can_register=False,
            prerequisites_met=False,
            corequisites_met=True,
            antirequisites_blocking=False,
        )
    )

    with pytest.raises(EnrollmentEligibilityError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_create_manual_enrollment_blocks_over_36_ects() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    service.course_offering_repo.get_by_id_with_course = AsyncMock(
        return_value=created.course_offering
    )
    service.eligibility_service.check_eligibility = AsyncMock(
        return_value=_eligible_response()
    )
    service.enrollment_repo.sum_active_ects = AsyncMock(return_value=32)
    service.enrollment_repo.list_active_offerings = AsyncMock(return_value=[])

    with pytest.raises(EnrollmentCreditsExceededError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_create_manual_enrollment_allows_overload_up_to_42() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    _setup_create_mocks(service, created.course_offering, created)
    service.enrollment_repo.sum_active_ects = AsyncMock(return_value=34)

    response = await service.create_manual_enrollment(1, 7, course_overload_acknowledged=True)

    assert response.status == "in_progress"


@pytest.mark.asyncio
async def test_create_manual_enrollment_blocks_schedule_conflict() -> None:
    service = EnrollmentService(session=None)
    created = make_enrollment("Fall", 2026)
    conflicting_offering = SimpleNamespace(
        id=10,
        course_id=99,
        days="MWF",
        meeting_time="10:00 AM - 10:50 AM",
        course=SimpleNamespace(id=99, code="BIO", level="101"),
    )
    service.course_offering_repo.get_by_id_with_course = AsyncMock(
        return_value=created.course_offering
    )
    service.eligibility_service.check_eligibility = AsyncMock(
        return_value=_eligible_response()
    )
    service.enrollment_repo.sum_active_ects = AsyncMock(return_value=0)
    service.enrollment_repo.list_active_offerings = AsyncMock(
        return_value=[conflicting_offering]
    )

    with pytest.raises(EnrollmentScheduleConflictError):
        await service.create_manual_enrollment(1, 7)


@pytest.mark.asyncio
async def test_delete_enrollment_removes_matching_identity() -> None:
    service = EnrollmentService(session=None)
    enrollment = make_enrollment("Fall", 2026)
    service.enrollment_repo.get_by_identity = AsyncMock(return_value=enrollment)
    service.enrollment_repo.delete = AsyncMock()
    service.assessment_repo.delete_by_user_and_course = AsyncMock()

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
