from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_onboarded_user
from nutrack.insights.dependencies import get_insights_service


@pytest.mark.asyncio
async def test_get_insights_returns_service_payload(
    client,
    test_app,
) -> None:
    user = SimpleNamespace(id=1, is_onboarded=True)
    service = SimpleNamespace(
        get_or_generate=AsyncMock(
            return_value={
                "short_summary": "Keep going.",
                "long_summary": "Paragraph 1.\n\nParagraph 2.",
                "actions": [],
                "generated_at": "2026-04-20T10:00:00Z",
                "cached": False,
            }
        )
    )
    test_app.dependency_overrides[get_current_onboarded_user] = lambda: user
    test_app.dependency_overrides[get_insights_service] = lambda: service

    response = await client.get("/v1/insights")

    assert response.status_code == 200
    assert response.json()["data"]["short_summary"] == "Keep going."
    service.get_or_generate.assert_awaited_once_with(1, user)
