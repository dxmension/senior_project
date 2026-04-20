from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.exc import IntegrityError

from nutrack.enrollments.exceptions import EnrollmentConflictError
from nutrack.enrollments.models import EnrollmentStatus
from nutrack.enrollments.service import (
    EnrollmentService,
    build_enrollment_response,
    format_course_code,
)


def _enrollment() -> SimpleNamespace:
    course = SimpleNamespace(
        id=5,
        code="CSCI",
        level="151",
        title="Programming",
        ects=6,
    )
    offering = SimpleNamespace(
        id=7,
        course_id=5,
        section="2",
        term="Fall",
        year=2026,
        meeting_time="10:00-10:50",
        room="6.310",
        course=course,
    )
    return SimpleNamespace(
        user_id=1,
        course_id=7,
        term="Fall",
        year=2026,
        grade="A",
        grade_points=4.0,
        status=EnrollmentStatus.PASSED,
        course_offering=offering,
    )


@pytest.mark.parametrize(
    ("code", "level", "expected"),
    [("CSCI", "151", "CSCI 151"), ("BIO101", "0", "BIO101"), ("NUSM", "0", "NUSM")],
)
def test_format_course_code_handles_special_cases(
    code: str,
    level: str,
    expected: str,
) -> None:
    assert format_course_code(code, level) == expected


def test_build_enrollment_response_maps_course_fields() -> None:
    response = build_enrollment_response(_enrollment())

    assert response.course_code == "CSCI 151"
    assert response.section == "2"
    assert response.status == "passed"
    assert response.meeting_time == "10:00-10:50"
    assert response.room == "6.310"


@pytest.mark.asyncio
async def test_create_translates_integrity_error_to_conflict() -> None:
    service = EnrollmentService(session=None)
    service.enrollment_repo.create = AsyncMock(
        side_effect=IntegrityError("stmt", "params", Exception("boom"))
    )

    with pytest.raises(EnrollmentConflictError):
        await service._create(1, 7, "Fall", 2026)  # noqa: SLF001


@pytest.mark.asyncio
async def test_load_returns_original_enrollment_when_reload_misses() -> None:
    service = EnrollmentService(session=None)
    enrollment = _enrollment()
    service.enrollment_repo.get_by_identity = AsyncMock(return_value=None)

    result = await service._load(1, 7, "Fall", 2026, enrollment)  # noqa: SLF001

    assert result is enrollment
