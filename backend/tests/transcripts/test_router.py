from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_user
from nutrack.transcripts.dependencies import get_transcript_service


@pytest.mark.asyncio
async def test_upload_transcript_returns_upload_status(
    client,
    test_app,
    current_user,
) -> None:
    service = SimpleNamespace(upload=AsyncMock(return_value="upload-1"))
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_transcript_service] = lambda: service

    response = await client.post(
        "/v1/transcripts/uploads",
        files={"file": ("transcript.pdf", b"pdf", "application/pdf")},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {
        "upload_id": "upload-1",
        "status": "completed",
    }


@pytest.mark.asyncio
async def test_upload_transcript_requires_auth(client, test_app) -> None:
    service = SimpleNamespace(upload=AsyncMock())
    test_app.dependency_overrides[get_transcript_service] = lambda: service

    response = await client.post(
        "/v1/transcripts/uploads",
        files={"file": ("transcript.pdf", b"pdf", "application/pdf")},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_upload_status_returns_service_payload(client, test_app) -> None:
    payload = {"upload_id": "upload-2", "status": "failed", "error": "bad file"}
    service = SimpleNamespace(get_upload_status=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_transcript_service] = lambda: service

    response = await client.get("/v1/transcripts/uploads/upload-2")

    assert response.status_code == 200
    assert response.json()["data"] == payload


@pytest.mark.asyncio
async def test_manual_transcript_routes_require_auth(client, test_app) -> None:
    service = SimpleNamespace(save_manual_entries=AsyncMock())
    test_app.dependency_overrides[get_transcript_service] = lambda: service
    payload = {
        "major": "Computer Science",
        "courses": [
            {
                "code": "CSCI 151",
                "title": "Programming",
                "term": "Fall",
                "year": 2025,
                "grade": "A",
                "grade_points": 4.0,
                "ects": 6,
            }
        ],
    }

    save_response = await client.post("/v1/transcripts/manual", json=payload)
    confirm_response = await client.post("/v1/transcripts/confirm", json=payload)

    assert save_response.status_code == 401
    assert confirm_response.status_code == 401


@pytest.mark.asyncio
async def test_confirm_transcript_returns_confirmed_flag(
    client,
    test_app,
    current_user,
) -> None:
    service = SimpleNamespace(save_manual_entries=AsyncMock())
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_transcript_service] = lambda: service
    payload = {
        "major": "Computer Science",
        "courses": [
            {
                "code": "CSCI 151",
                "title": "Programming",
                "term": "Fall",
                "year": 2025,
                "grade": "A",
                "grade_points": 4.0,
                "ects": 6,
            }
        ],
    }

    response = await client.post("/v1/transcripts/confirm", json=payload)

    assert response.status_code == 200
    assert response.json()["data"] == {"confirmed": True}
    service.save_manual_entries.assert_awaited_once()

