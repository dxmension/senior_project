from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_admin_user
from nutrack.courses.dependencies import get_course_schedule_service


@pytest.mark.asyncio
async def test_upload_course_schedule_returns_summary(client, test_app) -> None:
    payload = {
        "term": "Fall",
        "year": 2026,
        "processed_rows": 2,
        "inserted_count": 1,
        "updated_count": 1,
        "invalid_rows_count": 0,
        "invalid_rows": [],
    }
    service = SimpleNamespace(ingest=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_current_admin_user] = lambda: object()
    test_app.dependency_overrides[get_course_schedule_service] = lambda: service

    response = await client.post(
        "/v1/courses/schedule/upload?term=Fall&year=2026",
        files={"file": ("schedule.pdf", b"pdf", "application/pdf")},
    )

    assert response.status_code == 201
    assert response.json()["data"] == payload
    file_arg, term_arg, year_arg = service.ingest.await_args.args
    assert file_arg.filename == "schedule.pdf"
    assert term_arg == "Fall"
    assert year_arg == 2026


@pytest.mark.asyncio
async def test_upload_course_schedule_requires_admin(client, test_app) -> None:
    service = SimpleNamespace(ingest=AsyncMock())
    test_app.dependency_overrides[get_course_schedule_service] = lambda: service

    response = await client.post(
        "/v1/courses/schedule/upload?term=Fall&year=2026",
        files={"file": ("schedule.pdf", b"pdf", "application/pdf")},
    )

    assert response.status_code == 401

