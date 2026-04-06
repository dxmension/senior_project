from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from nutrack.admin.exceptions import UserNotFoundError
from nutrack.admin.service import AdminService


class _UserWithoutLazyEnrollments:
    def __init__(self) -> None:
        now = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.id = 1
        self.email = "student@nu.edu.kz"
        self.google_id = "google-1"
        self.first_name = "John"
        self.last_name = "Doe"
        self.major = "Computer Science"
        self.study_year = 3
        self.cgpa = 3.8
        self.total_credits_earned = 42
        self.total_credits_enrolled = 48
        self.avatar_url = None
        self.is_onboarded = True
        self.is_admin = False
        self.created_at = now
        self.updated_at = now

    @property
    def enrollments(self):
        raise AssertionError("service should not lazy-load enrollments")


@pytest.mark.asyncio
async def test_get_user_detail_uses_explicit_enrollment_count() -> None:
    repository = AsyncMock()
    repository.get_user_by_id.return_value = _UserWithoutLazyEnrollments()
    repository.get_user_enrollment_count.return_value = 3
    service = AdminService(repository=repository, redis=AsyncMock())

    result = await service.get_user_detail(1)

    assert result.enrollment_count == 3
    repository.get_user_enrollment_count.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_user_detail_raises_when_user_missing() -> None:
    repository = AsyncMock()
    repository.get_user_by_id.return_value = None
    service = AdminService(repository=repository, redis=AsyncMock())

    with pytest.raises(UserNotFoundError):
        await service.get_user_detail(1)
