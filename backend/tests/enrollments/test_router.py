from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_user
from nutrack.enrollments.dependencies import get_enrollment_service
from nutrack.enrollments.exceptions import EnrollmentConflictError
from nutrack.enrollments.schemas import EnrollmentItemResponse


def enrollment_item() -> EnrollmentItemResponse:
    return EnrollmentItemResponse(
        user_id=1,
        course_id=7,
        catalog_course_id=4,
        course_code="CSCI 151",
        section="2",
        course_title="Programming",
        ects=6,
        grade=None,
        grade_points=None,
        term="Fall",
        year=2026,
        status="in_progress",
        meeting_time="10:00-10:50",
        room="6.310",
    )


@pytest.mark.asyncio
async def test_get_enrollments_returns_filtered_user_rows(
    client,
    test_app,
    current_user,
) -> None:
    service = SimpleNamespace(
        list_enrollments=AsyncMock(return_value=[enrollment_item()])
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_enrollment_service] = lambda: service

    response = await client.get("/v1/enrollments?status=in_progress")

    assert response.status_code == 200
    assert response.json()["data"][0]["course_id"] == 7
    assert response.json()["data"][0]["catalog_course_id"] == 4
    assert response.json()["data"][0]["term"] == "Fall"
    service.list_enrollments.assert_awaited_once()


@pytest.mark.asyncio
async def test_post_enrollments_returns_created_item(
    client,
    test_app,
    current_user,
) -> None:
    service = SimpleNamespace(
        create_manual_enrollment=AsyncMock(return_value=enrollment_item()),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_enrollment_service] = lambda: service

    response = await client.post("/v1/enrollments", json={"course_id": 7})

    assert response.status_code == 201
    assert response.json()["data"]["course_code"] == "CSCI 151"


@pytest.mark.asyncio
async def test_post_enrollments_returns_conflict_for_duplicates(
    client,
    test_app,
    current_user,
) -> None:
    service = SimpleNamespace(
        create_manual_enrollment=AsyncMock(side_effect=EnrollmentConflictError()),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_enrollment_service] = lambda: service

    response = await client.post("/v1/enrollments", json={"course_id": 7})

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_enrollment_returns_deleted_flag(
    client,
    test_app,
    current_user,
) -> None:
    service = SimpleNamespace(delete_enrollment=AsyncMock())
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_enrollment_service] = lambda: service

    response = await client.delete("/v1/enrollments/7?term=Fall&year=2026")

    assert response.status_code == 200
    assert response.json()["data"] == {"deleted": True}


@pytest.mark.asyncio
async def test_enrollment_endpoints_require_auth(client, test_app) -> None:
    fake = enrollment_item()
    service = SimpleNamespace(
        list_enrollments=AsyncMock(return_value=[fake]),
        create_manual_enrollment=AsyncMock(return_value=fake),
        delete_enrollment=AsyncMock(),
    )
    test_app.dependency_overrides[get_enrollment_service] = lambda: service

    get_response = await client.get("/v1/enrollments")
    post_response = await client.post("/v1/enrollments", json={"course_id": 7})
    delete_response = await client.delete("/v1/enrollments/7?term=Fall&year=2026")

    assert get_response.status_code == 401
    assert post_response.status_code == 401
    assert delete_response.status_code == 401
