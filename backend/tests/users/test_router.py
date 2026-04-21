from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_user
from nutrack.users.dependencies import get_user_service


def _profile() -> dict[str, object]:
    return {
        "id": 1,
        "email": "student@nu.edu.kz",
        "first_name": "John",
        "last_name": "Doe",
        "avatar_url": None,
        "major": "Computer Science",
        "study_year": 3,
        "cgpa": 3.8,
        "total_credits_earned": 42,
        "total_credits_enrolled": 48,
        "is_onboarded": True,
        "subscribed_to_notifications": True,
        "created_at": datetime(2026, 1, 1).isoformat(),
    }


@pytest.mark.asyncio
async def test_get_profile_returns_service_payload(client, test_app, current_user) -> None:
    service = SimpleNamespace(get_profile=AsyncMock(return_value=_profile()))
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_user_service] = lambda: service

    response = await client.get("/v1/profile")

    assert response.status_code == 200
    assert response.json()["data"]["email"] == "student@nu.edu.kz"


@pytest.mark.asyncio
async def test_update_profile_passes_body_to_service(client, test_app, current_user) -> None:
    service = SimpleNamespace(update_profile=AsyncMock(return_value=_profile()))
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_user_service] = lambda: service

    response = await client.patch(
        "/v1/profile",
        json={"major": "Biology", "study_year": 4, "subscribed_to_notifications": False},
    )

    assert response.status_code == 200
    body_arg = service.update_profile.await_args.args[1]
    assert body_arg.major == "Biology"
    assert body_arg.study_year == 4
    assert body_arg.subscribed_to_notifications is False


@pytest.mark.asyncio
async def test_get_profile_routes_require_auth(client, test_app) -> None:
    service = SimpleNamespace(
        get_profile=AsyncMock(return_value=_profile()),
        update_profile=AsyncMock(return_value=_profile()),
        get_enrollments=AsyncMock(return_value=[]),
        get_stats=AsyncMock(return_value={"total_credits": 0, "completed_courses": 0, "semesters_completed": 0}),
    )
    test_app.dependency_overrides[get_user_service] = lambda: service

    get_response = await client.get("/v1/profile")
    patch_response = await client.patch("/v1/profile", json={"major": "CS"})
    enrollments_response = await client.get("/v1/profile/enrollments")
    stats_response = await client.get("/v1/profile/stats")

    assert get_response.status_code == 401
    assert patch_response.status_code == 401
    assert enrollments_response.status_code == 401
    assert stats_response.status_code == 401


@pytest.mark.asyncio
async def test_get_stats_returns_aggregated_payload(
    client,
    test_app,
    current_user,
) -> None:
    payload = {
        "total_credits": 42,
        "completed_courses": 7,
        "current_gpa": 3.8,
        "semesters_completed": 3,
        "credits_by_semester": [
            {
                "semester": "Spring 2025",
                "term": "Spring",
                "year": 2025,
                "credits": 18,
            }
        ],
    }
    service = SimpleNamespace(
        get_profile=AsyncMock(),
        update_profile=AsyncMock(),
        get_enrollments=AsyncMock(return_value=[]),
        get_stats=AsyncMock(return_value=payload),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_user_service] = lambda: service

    response = await client.get("/v1/profile/stats")

    assert response.status_code == 200
    assert response.json()["data"]["completed_courses"] == 7
