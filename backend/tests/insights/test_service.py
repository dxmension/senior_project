from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.insights.schemas import ActionSuggestion, InsightLLMResponse, InsightsResponse
from nutrack.insights.service import InsightsService, _build_user_prompt, _route_options


def _user() -> SimpleNamespace:
    return SimpleNamespace(first_name="Amina", major="Computer Science", cgpa=3.67)


def _context() -> dict:
    return {
        "student": {
            "first_name": "Amina",
            "major": "Computer Science",
            "cgpa": 3.67,
            "study_year": 2,
            "total_years": 4,
            "study_progress": "2/4",
            "term": "Spring",
            "year": 2026,
        },
        "courses": [
            {
                "course_id": 42,
                "course_code": "CSCI 151",
                "course_title": "Programming for Scientists",
                "ects": 5,
                "assessment_avg_pct": 64.5,
                "mock_avg_pct": 55.0,
                "overdue_count": 1,
                "study_metadata": {
                    "mock_exam_count": 1,
                    "flashcard_deck_count": 1,
                    "mindmap_count": 1,
                },
                "route_options": [
                    {
                        "action_type": "take_midterm",
                        "label": "Midterm 1",
                        "action_url": "/study/42/midterm/1",
                    },
                    {
                        "action_type": "start_flashcards",
                        "label": "Open flashcards",
                        "action_url": "/study/42?tab=flashcards",
                    },
                    {
                        "action_type": "view_mindmap",
                        "label": "Open mindmaps",
                        "action_url": "/study/42?tab=mindmaps",
                    },
                ],
            }
        ],
        "overdue_items": [
            {
                "course_code": "CSCI 151",
                "assessment_type": "quiz",
                "assessment_number": 2,
                "days_overdue": 3,
            }
        ],
        "flashcards": [
            {
                "course_code": "CSCI 151",
                "deck_title": "Pointers",
                "hard_rate": 42.0,
                "times_seen": 30,
            }
        ],
        "history": [{"course_code": "MATH 161", "grade": "A-", "grade_points": 3.67}],
        "weak_signals": ["CSCI 151 mock avg 55.0%"],
    }


def _llm_payload() -> InsightLLMResponse:
    return InsightLLMResponse(
        short_summary="Amina, you're making progress. Keep the momentum this week.",
        long_summary="Paragraph 1.\n\nParagraph 2.\n\nParagraph 3.\n\nParagraph 4.",
        actions=[
            ActionSuggestion(
                label="Practice Midterm 1",
                description="Revisit the weakest family first.",
                action_type="take_midterm",
                action_url="/study/42/midterm/1",
            ),
            ActionSuggestion(
                label="Bad action",
                description="Should be removed.",
                action_type="view_mindmap",
                action_url="https://example.com",
            ),
            ActionSuggestion(
                label="Invented route",
                description="Should also be removed.",
                action_type="take_midterm",
                action_url="/study/999/midterm/9",
            ),
        ],
    )


@pytest.mark.asyncio
async def test_get_or_generate_returns_cached_payload() -> None:
    service = InsightsService(session=None, redis=AsyncMock())
    cached = InsightsResponse(
        short_summary="Cached",
        long_summary="Cached long",
        actions=[],
        generated_at=datetime(2026, 4, 20, tzinfo=timezone.utc),
        cached=False,
    )
    service.redis.get.return_value = cached.model_dump_json()

    result = await service.get_or_generate(7, _user())

    assert result.cached is True
    assert result.short_summary == "Cached"
    service.redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_generate_saves_new_payload(monkeypatch) -> None:
    service = InsightsService(session=None, redis=AsyncMock())
    service.redis.get.return_value = None
    service._aggregate_context = AsyncMock(return_value=_context())  # type: ignore[method-assign]
    monkeypatch.setattr(
        "nutrack.insights.service.parse_structured_response",
        AsyncMock(return_value=_llm_payload()),
    )

    result = await service.get_or_generate(7, _user())

    assert result.cached is False
    assert len(result.actions) == 1
    service.redis.setex.assert_awaited_once()
    assert service.redis.setex.await_args.args[:2] == ("ai_insights:7", 86400)


@pytest.mark.asyncio
async def test_get_or_generate_waits_for_existing_inflight_result() -> None:
    service = InsightsService(session=None, redis=AsyncMock())
    cached = InsightsResponse(
        short_summary="Ready",
        long_summary="Generated elsewhere",
        actions=[],
        generated_at=datetime(2026, 4, 20, tzinfo=timezone.utc),
        cached=False,
    )
    service.redis.get.side_effect = [
        None,
        None,
        cached.model_dump_json(),
    ]
    service.redis.set.return_value = None
    service.redis.exists.side_effect = [1, 1]

    result = await service.get_or_generate(7, _user())

    assert result.short_summary == "Ready"
    assert result.cached is True
    service.redis.setex.assert_not_called()


@pytest.mark.asyncio
async def test_waiter_retries_generation_after_lock_clears(monkeypatch) -> None:
    service = InsightsService(session=None, redis=AsyncMock())
    service.redis.get.side_effect = lambda key: None
    service.redis.set.side_effect = [None, True]
    service.redis.exists.return_value = 0
    generated = InsightsResponse(
        short_summary="Fresh",
        long_summary="Fresh long",
        actions=[],
        generated_at=datetime(2026, 4, 20, tzinfo=timezone.utc),
        cached=False,
    )
    service._generate_insights = AsyncMock(return_value=generated)  # type: ignore[method-assign]

    result = await service.get_or_generate(7, _user())

    assert result.short_summary == "Fresh"
    service._generate_insights.assert_awaited_once()
    service.redis.setex.assert_awaited_once()


def test_build_user_prompt_keeps_allowed_routes() -> None:
    prompt = _build_user_prompt(_context())

    assert "Allowed actions:" in prompt
    assert "/study/42/midterm/1" in prompt
    assert "/study/42?tab=flashcards" in prompt
    assert "/study/42?tab=mindmaps" in prompt
    assert "study_year=2" in prompt
    assert "total_years=4" in prompt
    assert "study_progress=2/4" in prompt
    assert "available[mock=1, flashcards=1, mindmaps=1]" in prompt
    assert len(prompt) <= 2000


def test_route_options_falls_back_to_course_study_page() -> None:
    routes = _route_options(
        42,
        [],
        {
            "mock_exam_count": 0,
            "mock_families": set(),
            "flashcard_deck_count": 0,
            "mindmap_count": 0,
        },
    )

    assert routes == [
        {
            "action_type": "take_mock",
            "label": "Review study tools",
            "action_url": "/study/42",
        }
    ]
