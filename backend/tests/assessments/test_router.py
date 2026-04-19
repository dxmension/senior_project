from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.assessments.dependencies import get_assessment_service
from nutrack.auth.dependencies import get_current_user


def _assessment_payload() -> dict:
    return {
        "id": 7,
        "course_id": 4,
        "course_code": "BIOL 101",
        "course_title": "Introductory Biology",
        "assessment_type": "midterm",
        "assessment_number": 2,
        "title": "Midterm 2",
        "description": "Focus on chapters 1-4",
        "deadline": "2026-04-20T00:00:00Z",
        "weight": 25.0,
        "score": None,
        "max_score": 100.0,
        "is_completed": False,
        "created_at": "2026-04-01T00:00:00Z",
        "updated_at": "2026-04-02T00:00:00Z",
    }


@pytest.mark.asyncio
async def test_list_assessments_returns_numbered_payload(
    client,
    current_user,
    test_app,
) -> None:
    service = SimpleNamespace(
        list_assessments=AsyncMock(return_value=[_assessment_payload()]),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_assessment_service] = lambda: service

    response = await client.get("/v1/assessments?course_id=4")

    assert response.status_code == 200
    assert response.json()["data"][0]["assessment_number"] == 2
    assert response.json()["data"][0]["title"] == "Midterm 2"


@pytest.mark.asyncio
async def test_create_assessment_accepts_assessment_number(
    client,
    current_user,
    test_app,
) -> None:
    service = SimpleNamespace(
        create_assessment=AsyncMock(return_value=_assessment_payload()),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_assessment_service] = lambda: service

    response = await client.post(
        "/v1/assessments",
        json={
            "course_id": 4,
            "assessment_type": "midterm",
            "assessment_number": 2,
            "deadline": "2026-04-20T00:00:00Z",
            "weight": 25,
            "max_score": 100,
        },
    )

    assert response.status_code == 201
    assert response.json()["data"]["title"] == "Midterm 2"
    service.create_assessment.assert_awaited_once()
