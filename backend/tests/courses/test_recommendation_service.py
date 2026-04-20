"""Tests for CourseRecommendationService."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from nutrack.courses.recommendation_service import (
    CourseRecommendationService,
    _next_semester,
)
from nutrack.courses.schemas import RecommendationsResponse


def test_next_semester_spring():
    term, year = _next_semester("Spring", 2026)
    assert term == "Fall"
    assert year == 2026


def test_next_semester_fall():
    term, year = _next_semester("Fall", 2026)
    assert term == "Spring"
    assert year == 2027


def test_next_semester_summer():
    term, year = _next_semester("Summer", 2026)
    assert term == "Fall"
    assert year == 2026


@pytest.fixture()
def mock_service():
    course_repo = AsyncMock()
    offering_repo = AsyncMock()
    gpa_stats_repo = AsyncMock()
    eligibility_svc = AsyncMock()

    with patch(
        "nutrack.courses.recommendation_service.AsyncOpenAI"
    ) as mock_openai_cls:
        mock_openai_cls.return_value = MagicMock()
        svc = CourseRecommendationService(
            course_repository=course_repo,
            offering_repository=offering_repo,
            gpa_stats_repository=gpa_stats_repo,
            eligibility_service=eligibility_svc,
        )
        yield svc, course_repo, offering_repo, gpa_stats_repo, eligibility_svc


@pytest.mark.asyncio
async def test_returns_empty_when_no_next_term_offerings(mock_service):
    svc, course_repo, offering_repo, gpa_stats_repo, elig_svc = mock_service

    user = MagicMock()
    user.id = 1
    user.major = "Computer Science"
    user.cgpa = 3.5
    user.study_year = 3
    user.total_credits_earned = 90
    user.kazakh_level = None

    course_repo.get_user_course_history.return_value = []
    offering_repo.list_by_term.return_value = []

    result = await svc.get_recommendations(user)

    assert isinstance(result, RecommendationsResponse)
    assert result.recommendations == []


@pytest.mark.asyncio
async def test_skips_already_taken_courses(mock_service):
    svc, course_repo, offering_repo, gpa_stats_repo, elig_svc = mock_service

    user = MagicMock()
    user.id = 1
    user.major = "Computer Science"
    user.cgpa = 3.0
    user.study_year = 2
    user.total_credits_earned = 60
    user.kazakh_level = None

    # History: catalog course id=5 already taken
    course_repo.get_user_course_history.return_value = [
        {
            "id": 5,
            "code": "CSCI",
            "level": "151",
            "grade": "A",
            "grade_points": 4.0,
            "status": "passed",
            "term": "Fall",
            "year": 2024,
        }
    ]

    # Next-term offering for the same catalog course (course_id=5) → must be filtered
    mock_off = MagicMock()
    mock_off.course_id = 5
    mock_off.id = 101
    offering_repo.list_by_term.return_value = [mock_off]

    result = await svc.get_recommendations(user)

    assert result.recommendations == []
    elig_svc.check_eligibility.assert_not_called()


@pytest.mark.asyncio
async def test_returns_empty_when_no_eligible_courses(mock_service):
    svc, course_repo, offering_repo, gpa_stats_repo, elig_svc = mock_service

    user = MagicMock()
    user.id = 1
    user.major = "Computer Science"
    user.cgpa = 2.0
    user.study_year = 1
    user.total_credits_earned = 30
    user.kazakh_level = None

    course_repo.get_user_course_history.return_value = []

    mock_off = MagicMock()
    mock_off.course_id = 10
    mock_off.id = 200
    offering_repo.list_by_term.return_value = [mock_off]

    # Eligibility check fails for every course
    elig_result = MagicMock()
    elig_result.can_register = False
    elig_svc.check_eligibility.return_value = elig_result

    result = await svc.get_recommendations(user)

    assert result.recommendations == []
