from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_user
from nutrack.courses.dependencies import get_course_search_service


@pytest.mark.asyncio
async def test_get_courses_returns_filtered_options(
    client,
    test_app,
    current_user,
) -> None:
    options = [
        {
            "id": 7,
            "code": "CSCI",
            "level": "151",
            "section": "2",
            "title": "Programming",
            "ects": 6,
            "term": "Spring",
            "year": 2026,
            "meeting_time": "10:00-10:50",
            "room": "6.310",
        }
    ]
    service = SimpleNamespace(search_courses=AsyncMock(return_value=options))
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_course_search_service] = lambda: service

    response = await client.get("/v1/courses?q=cs&limit=10")

    assert response.status_code == 200
    assert response.json()["data"][0]["code"] == "CSCI"
    assert response.json()["data"][0]["section"] == "2"
    assert response.json()["data"][0]["year"] == 2026
    service.search_courses.assert_awaited_once_with("cs", 10, None, None)


@pytest.mark.asyncio
async def test_get_courses_requires_auth(client, test_app) -> None:
    service = SimpleNamespace(search_courses=AsyncMock(return_value=[]))
    test_app.dependency_overrides[get_course_search_service] = lambda: service

    response = await client.get("/v1/courses?q=cs")

    assert response.status_code == 401
