"""Tests for CourseRecommendationService."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.config import settings
from nutrack.courses.recommendation_service import CourseRecommendationService
from nutrack.courses.schemas import RecommendationsResponse


def test_uses_current_semester_settings():
    assert settings.CURRENT_TERM == "Spring"
    assert settings.CURRENT_YEAR == 2026


@pytest.fixture()
def mock_service():
    course_repo = AsyncMock()
    offering_repo = AsyncMock()
    gpa_stats_repo = AsyncMock()
    eligibility_svc = AsyncMock()
    handbook_svc = AsyncMock()
    service = CourseRecommendationService(
        course_repository=course_repo,
        offering_repository=offering_repo,
        gpa_stats_repository=gpa_stats_repo,
        eligibility_service=eligibility_svc,
        handbook_service=handbook_svc,
    )
    return (
        service,
        course_repo,
        offering_repo,
        gpa_stats_repo,
        eligibility_svc,
        handbook_svc,
    )


def make_offering(course_id: int, code: str, level: str, title: str):
    course = SimpleNamespace(
        id=course_id,
        code=code,
        level=level,
        title=title,
        ects=6,
        description=None,
        department=code,
        priority_1=None,
        priority_2=None,
        priority_3=None,
        priority_4=None,
    )
    return SimpleNamespace(
        id=course_id * 10,
        course_id=course_id,
        course=course,
        section="1L",
        faculty="Faculty",
        meeting_time="10:00 AM-10:50 AM",
        days="M W",
        room="7.101",
        enrolled=10,
        capacity=20,
    )


@pytest.mark.asyncio
async def test_returns_empty_when_no_current_term_offerings(mock_service):
    svc, course_repo, offering_repo, _, _, handbook_svc = mock_service
    user = SimpleNamespace(
        id=1,
        major="Computer Science",
        cgpa=3.5,
        study_year=3,
        total_credits_earned=90,
        kazakh_level=None,
    )
    course_repo.get_user_course_history.return_value = []
    handbook_svc.get_plans_for_year.return_value = None
    offering_repo.list_by_term.return_value = []

    result = await svc.get_recommendations(user)

    assert isinstance(result, RecommendationsResponse)
    assert result.recommendations == []
    offering_repo.list_by_term.assert_awaited_once_with("Spring", 2026, limit=None)


@pytest.mark.asyncio
async def test_skips_already_taken_courses(mock_service):
    svc, course_repo, offering_repo, _, elig_svc, handbook_svc = mock_service
    user = SimpleNamespace(
        id=1,
        major="Computer Science",
        cgpa=3.0,
        study_year=2,
        total_credits_earned=60,
        kazakh_level=None,
    )
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
    handbook_svc.get_plans_for_year.return_value = None
    offering_repo.list_by_term.return_value = [make_offering(5, "CSCI", "151", "Intro")]

    result = await svc.get_recommendations(user)

    assert result.recommendations == []
    elig_svc.check_eligibility.assert_not_called()


@pytest.mark.asyncio
async def test_recommends_exact_missing_audit_courses_for_cs(mock_service):
    svc, course_repo, offering_repo, gpa_repo, elig_svc, handbook_svc = mock_service
    user = SimpleNamespace(
        id=1,
        major="Computer Science",
        cgpa=2.96,
        study_year=4,
        total_credits_earned=230,
        kazakh_level=None,
    )
    course_repo.get_user_course_history.return_value = [
        {
            "id": 245,
            "code": "CSCI",
            "level": "245",
            "grade": None,
            "grade_points": None,
            "status": "in_progress",
            "term": "Spring",
            "year": 2026,
        },
        {
            "id": 408,
            "code": "CSCI",
            "level": "408",
            "grade": "B",
            "grade_points": 3.0,
            "status": "passed",
            "term": "Fall",
            "year": 2025,
        },
        {
            "id": 201,
            "code": "KAZ",
            "level": "201",
            "grade": "B+",
            "grade_points": 3.33,
            "status": "passed",
            "term": "Fall",
            "year": 2023,
        },
    ]
    handbook_svc.get_plans_for_year.return_value = {
        "computer science": {
            "total_ects": 240,
            "categories": [
                {
                    "name": "Computer Science Core",
                    "requirements": [
                        {
                            "name": "Research Methods",
                            "patterns": ["CSCI 307"],
                            "required_count": 1,
                            "ects_per_course": 6,
                            "is_elective": False,
                            "note": "",
                        }
                    ],
                },
                {
                    "name": "Capstone",
                    "requirements": [
                        {
                            "name": "Senior Project I",
                            "patterns": ["CSCI 408"],
                            "required_count": 1,
                            "ects_per_course": 6,
                            "is_elective": False,
                            "note": "",
                        },
                        {
                            "name": "Senior Project II",
                            "patterns": ["CSCI 409"],
                            "required_count": 1,
                            "ects_per_course": 6,
                            "is_elective": False,
                            "note": "",
                        },
                    ],
                },
                {
                    "name": "University Core",
                    "requirements": [
                        {
                            "name": "Kazakh Language II",
                            "patterns": ["KAZ 300"],
                            "required_count": 1,
                            "ects_per_course": 6,
                            "is_elective": False,
                            "note": "",
                        }
                    ],
                },
                {
                    "name": "University Electives",
                    "requirements": [
                        {
                            "name": "Technical Elective",
                            "patterns": ["CSCI 2", "CSCI 3", "CSCI 4"],
                            "required_count": 1,
                            "ects_per_course": 6,
                            "is_elective": True,
                            "note": "",
                        }
                    ],
                },
            ],
        }
    }
    offering_repo.list_by_term.return_value = [
        make_offering(307, "CSCI", "307", "Research Methods"),
        make_offering(409, "CSCI", "409", "Senior Project II"),
        make_offering(300, "KAZ", "300", "Kazakh Studies in the Post-Colonial Era"),
        make_offering(380, "CHEM", "380", "Research Methods"),
        make_offering(431, "CHEM", "431", "Computational Chemistry"),
    ]
    gpa_repo.get_avg_gpa_by_course_ids.return_value = {
        307: 3.2,
        409: 3.1,
        300: 3.0,
        380: 3.8,
        431: 3.9,
    }
    elig_svc.check_eligibility.return_value = SimpleNamespace(can_register=True)

    result = await svc.get_recommendations(user)

    codes = [(item.code, item.level) for item in result.recommendations]
    assert ("CSCI", "307") in codes
    assert ("CSCI", "409") in codes
    assert ("KAZ", "300") in codes
    assert ("CHEM", "380") not in codes
    assert ("CHEM", "431") not in codes


@pytest.mark.asyncio
async def test_prefers_kaz_3xx_for_broad_kazakh_requirement(mock_service):
    svc, course_repo, offering_repo, gpa_repo, elig_svc, handbook_svc = mock_service
    user = SimpleNamespace(
        id=1,
        major="Computer Science",
        cgpa=3.0,
        study_year=4,
        total_credits_earned=220,
        kazakh_level="C1",
    )
    course_repo.get_user_course_history.return_value = [
        {
            "id": 374,
            "code": "KAZ",
            "level": "374",
            "grade": "B",
            "grade_points": 3.0,
            "status": "passed",
            "term": "Fall",
            "year": 2025,
        }
    ]
    handbook_svc.get_plans_for_year.return_value = {
        "computer science": {
            "total_ects": 240,
            "categories": [
                {
                    "name": "University Core",
                    "requirements": [
                        {
                            "name": "Kazakh Language",
                            "patterns": ["KAZ"],
                            "required_count": 2,
                            "ects_per_course": 6,
                            "is_elective": False,
                            "note": "2 Kazakh Language courses",
                        }
                    ],
                }
            ],
        }
    }
    offering_repo.list_by_term.return_value = [
        make_offering(201, "KAZ", "201", "Academic Kazakh I"),
        make_offering(300, "KAZ", "300", "Kazakh Studies in the Post-Colonial Era"),
        make_offering(356, "KAZ", "356", "Kazakh Music History"),
    ]
    gpa_repo.get_avg_gpa_by_course_ids.return_value = {
        201: 2.8,
        300: 3.0,
        356: 3.7,
    }
    elig_svc.check_eligibility.return_value = SimpleNamespace(can_register=True)

    result = await svc.get_recommendations(user)

    assert result.recommendations[0].code == "KAZ"
    assert result.recommendations[0].level.startswith("3")


@pytest.mark.asyncio
async def test_returns_multiple_options_for_broad_requirements(mock_service):
    svc, course_repo, offering_repo, gpa_repo, elig_svc, handbook_svc = mock_service
    user = SimpleNamespace(
        id=1,
        major="Computer Science",
        cgpa=3.1,
        study_year=4,
        total_credits_earned=220,
        kazakh_level="C1",
    )
    course_repo.get_user_course_history.return_value = []
    handbook_svc.get_plans_for_year.return_value = {
        "computer science": {
            "total_ects": 240,
            "categories": [
                {
                    "name": "Electives",
                    "requirements": [
                        {
                            "name": "Technical Electives",
                            "patterns": ["CSCI 2", "CSCI 3", "CSCI 4", "PHYS 270"],
                            "required_count": 1,
                            "ects_per_course": 6,
                            "is_elective": True,
                            "note": "",
                        }
                    ],
                }
            ],
        }
    }
    offering_repo.list_by_term.return_value = [
        make_offering(245, "CSCI", "245", "System Analysis and Design"),
        make_offering(262, "CSCI", "262", "Software Project Management"),
        make_offering(270, "PHYS", "270", "Scientific Computing"),
        make_offering(363, "CSCI", "363", "Software Testing"),
    ]
    gpa_repo.get_avg_gpa_by_course_ids.return_value = {
        245: 3.0,
        262: 3.1,
        270: 3.2,
        363: 3.15,
    }
    elig_svc.check_eligibility.return_value = SimpleNamespace(can_register=True)

    result = await svc.get_recommendations(user)

    tech_codes = {(item.code, item.level) for item in result.recommendations}
    assert len(result.recommendations) >= 3
    assert ("CSCI", "245") in tech_codes or ("CSCI", "262") in tech_codes


@pytest.mark.asyncio
async def test_build_audit_passes_user_kazakh_level(monkeypatch, mock_service):
    svc, course_repo, _, _, _, handbook_svc = mock_service
    user = SimpleNamespace(
        id=1,
        major="Computer Science",
        cgpa=3.1,
        study_year=4,
        total_credits_earned=220,
        kazakh_level="B1",
    )
    history = [
        {
            "code": "CSCI",
            "level": "151",
            "status": "passed",
        }
    ]
    course_repo.get_user_course_history.return_value = history
    handbook_svc.get_plans_for_year.return_value = None

    captured: dict[str, object] = {}

    def fake_compute_audit(
        major,
        audit_input,
        earned,
        handbook_plans,
        *,
        kazakh_level=None,
    ):
        captured["major"] = major
        captured["audit_input"] = audit_input
        captured["earned"] = earned
        captured["handbook_plans"] = handbook_plans
        captured["kazakh_level"] = kazakh_level
        return SimpleNamespace(supported=False, categories=[])

    monkeypatch.setattr(
        "nutrack.courses.recommendation_service.compute_audit",
        fake_compute_audit,
    )

    await svc._build_audit(user, history)  # noqa: SLF001

    assert captured["kazakh_level"] == "B1"
