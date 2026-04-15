"""
Tests for catalog list, detail, and stats endpoints.

Strategy:
  - dependency_overrides replaces auth + service deps — no DB, no filesystem.
  - CourseCatalogService and CourseStatsService are replaced with SimpleNamespace
    stubs backed by AsyncMock.
  - Tests verify HTTP contract: status codes, response shape, field values.
"""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_admin_user, get_current_user
from nutrack.courses.dependencies import (
    get_course_catalog_service,
    get_course_stats_service,
)

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

COURSE_DETAIL = SimpleNamespace(
    id=1,
    code="CSCI",
    level="151",
    title="Introduction to Programming",
    ects=6,
    description="Basics of programming in Python.",
    prerequisites=None,
    school="SSH",
    department="Computer Science",
    academic_level="UG",
    credits_us=3.0,
    pass_grade="D",
)

STATS = SimpleNamespace(
    course_id=1,
    code="CSCI",
    level="151",
    title="Introduction to Programming",
    total_enrollments=120,
    total_distinct_students=98,
    avg_gpa=3.12,
    pass_rate=87.5,
    withdraw_rate=4.2,
    grade_distribution=[
        SimpleNamespace(grade="A", count=30, percentage=25.0),
        SimpleNamespace(grade="B", count=40, percentage=33.3),
    ],
    terms_offered=["Spring 2024", "Fall 2024"],
)

@pytest.fixture
def admin_user():
    return SimpleNamespace(id=99, email="admin@nu.edu.kz", is_admin=True)


@pytest.fixture
def regular_user():
    return SimpleNamespace(id=1, email="student@nu.edu.kz", is_onboarded=True)


@pytest.fixture
def catalog_stub():
    return SimpleNamespace(
        list_courses=AsyncMock(return_value=([COURSE_DETAIL], 1)),
        get_course=AsyncMock(return_value=COURSE_DETAIL),
    )


@pytest.fixture
def stats_stub():
    return SimpleNamespace(
        get_stats=AsyncMock(return_value=STATS),
    )


# ---------------------------------------------------------------------------
# Catalog list
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_list_catalog_returns_courses(
    client, test_app, regular_user, catalog_stub
):
    test_app.dependency_overrides[get_current_user] = lambda: regular_user
    test_app.dependency_overrides[get_course_catalog_service] = lambda: catalog_stub

    response = await client.get("/v1/courses/catalog")

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert isinstance(body["data"], list)
    assert body["data"][0]["code"] == "CSCI"
    assert body["meta"]["total"] == 1


@pytest.mark.asyncio
async def test_list_catalog_passes_search_query(
    client, test_app, regular_user, catalog_stub
):
    test_app.dependency_overrides[get_current_user] = lambda: regular_user
    test_app.dependency_overrides[get_course_catalog_service] = lambda: catalog_stub

    await client.get("/v1/courses/catalog?q=intro&skip=0&limit=5")

    catalog_stub.list_courses.assert_awaited_once_with(
        skip=0, limit=5, search="intro"
    )


@pytest.mark.asyncio
async def test_list_catalog_rejects_oversized_limit(
    client, test_app, regular_user, catalog_stub
):
    test_app.dependency_overrides[get_current_user] = lambda: regular_user
    test_app.dependency_overrides[get_course_catalog_service] = lambda: catalog_stub

    response = await client.get("/v1/courses/catalog?limit=200")

    assert response.status_code == 422  # Pydantic Query(le=100) validation


# ---------------------------------------------------------------------------
# Course detail
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_course_detail_returns_course(
    client, test_app, regular_user, catalog_stub
):
    test_app.dependency_overrides[get_current_user] = lambda: regular_user
    test_app.dependency_overrides[get_course_catalog_service] = lambda: catalog_stub

    response = await client.get("/v1/courses/catalog/1")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["id"] == 1
    assert data["code"] == "CSCI"
    assert data["ects"] == 6
    catalog_stub.get_course.assert_awaited_once_with(1)


# ---------------------------------------------------------------------------
# Course stats
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_course_stats_returns_stats(
    client, test_app, regular_user, stats_stub
):
    test_app.dependency_overrides[get_current_user] = lambda: regular_user
    test_app.dependency_overrides[get_course_stats_service] = lambda: stats_stub

    response = await client.get("/v1/courses/catalog/1/stats")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["course_id"] == 1
    assert data["avg_gpa"] == 3.12
    assert data["pass_rate"] == 87.5
    assert data["total_enrollments"] == 120
    assert data["total_distinct_students"] == 98
    assert len(data["grade_distribution"]) == 2
    assert data["terms_offered"] == ["Spring 2024", "Fall 2024"]
    stats_stub.get_stats.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_course_stats_unauthenticated_returns_401(client, test_app, stats_stub):
    test_app.dependency_overrides[get_course_stats_service] = lambda: stats_stub

    response = await client.get("/v1/courses/catalog/1/stats")

    assert response.status_code == 401
