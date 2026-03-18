from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.enrollments.models import EnrollmentStatus
from nutrack.users.exceptions import NotFoundError
from nutrack.users.schemas import UserProfileUpdate
from nutrack.users.service import UserService


def _result_with(*items):
    unique_scalars = SimpleNamespace(all=lambda: list(items))
    scalars = SimpleNamespace(unique=lambda: unique_scalars)
    return SimpleNamespace(scalars=lambda: scalars)


def _user() -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        email="student@nu.edu.kz",
        first_name="John",
        last_name="Doe",
        avatar_url=None,
        major="Computer Science",
        study_year=3,
        cgpa=3.7,
        total_credits_earned=40,
        total_credits_enrolled=48,
        is_onboarded=True,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_get_profile_raises_when_user_missing() -> None:
    service = UserService(session=None)
    service.user_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await service.get_profile(1)


@pytest.mark.asyncio
async def test_update_profile_skips_empty_updates() -> None:
    service = UserService(session=None)
    user = _user()
    service.user_repo.get_by_id = AsyncMock(return_value=user)
    service.user_repo.update = AsyncMock()

    response = await service.update_profile(1, UserProfileUpdate())

    assert response.email == user.email
    service.user_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_get_enrollments_delegates_to_enrollment_service(monkeypatch) -> None:
    service = UserService(session=None)
    list_mock = AsyncMock(return_value=["row"])
    monkeypatch.setattr(
        "nutrack.users.service.EnrollmentService.list_enrollments",
        list_mock,
    )

    result = await service.get_enrollments(1)

    assert result == ["row"]
    list_mock.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_stats_aggregates_credits_and_semesters() -> None:
    service = UserService(session=SimpleNamespace(execute=AsyncMock()))
    user = _user()
    passed = SimpleNamespace(
        term="Spring",
        year=2025,
        status=EnrollmentStatus.PASSED,
        course_offering=SimpleNamespace(course=SimpleNamespace(ects=6)),
    )
    current = SimpleNamespace(
        term="Fall",
        year=2025,
        status=EnrollmentStatus.IN_PROGRESS,
        course_offering=SimpleNamespace(course=SimpleNamespace(ects=5)),
    )
    service.user_repo.get_by_id = AsyncMock(return_value=user)
    service.session.execute = AsyncMock(return_value=_result_with(passed, current))

    result = await service.get_stats(1)

    assert result.total_credits == 40
    assert result.completed_courses == 1
    assert result.semesters_completed == 2
    assert [item.semester for item in result.credits_by_semester] == [
        "Spring 2025",
        "Fall 2025",
    ]
