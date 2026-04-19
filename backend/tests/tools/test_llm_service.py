from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from pydantic import BaseModel

from nutrack.tools.llm.exceptions import (
    LLMConfigurationError,
    LLMIncompleteResponseError,
    LLMRefusalError,
    LLMResponseError,
)
from nutrack.tools.llm import service as llm_service


class DemoResponse(BaseModel):
    value: str


@pytest.fixture(autouse=True)
def reset_llm_client(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_service, "_client", None)
    monkeypatch.setattr(llm_service, "_client_key", None)


@pytest.mark.asyncio
async def test_parse_structured_response_returns_parsed_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parsed = DemoResponse(value="ok")
    fake_client = _fake_client(SimpleNamespace(output_parsed=parsed))
    monkeypatch.setattr(llm_service, "_get_client", lambda: fake_client)

    result = await llm_service.parse_structured_response(
        system_prompt="system",
        user_prompt="user",
        response_model=DemoResponse,
    )

    assert result == parsed


def test_get_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(llm_service.settings, "OPENAI_API_KEY", "")

    with pytest.raises(LLMConfigurationError):
        llm_service._get_client()


@pytest.mark.asyncio
async def test_parse_structured_response_raises_for_refusal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = SimpleNamespace(
        output_parsed=None,
        output=[{"content": [{"type": "refusal", "refusal": "blocked"}]}],
    )
    fake_client = _fake_client(response)
    monkeypatch.setattr(llm_service, "_get_client", lambda: fake_client)

    with pytest.raises(LLMRefusalError, match="blocked"):
        await llm_service.parse_structured_response(
            system_prompt="system",
            user_prompt="user",
            response_model=DemoResponse,
        )


@pytest.mark.asyncio
async def test_parse_structured_response_raises_for_incomplete_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    response = SimpleNamespace(
        output_parsed=None,
        status="incomplete",
        incomplete_details=SimpleNamespace(reason="max_output_tokens"),
        output=[],
    )
    fake_client = _fake_client(response)
    monkeypatch.setattr(llm_service, "_get_client", lambda: fake_client)

    with pytest.raises(LLMIncompleteResponseError, match="max_output_tokens"):
        await llm_service.parse_structured_response(
            system_prompt="system",
            user_prompt="user",
            response_model=DemoResponse,
        )


@pytest.mark.asyncio
async def test_parse_structured_response_wraps_sdk_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake_client = _fake_client(error=RuntimeError("boom"))
    monkeypatch.setattr(llm_service, "_get_client", lambda: fake_client)

    with pytest.raises(LLMResponseError, match="boom"):
        await llm_service.parse_structured_response(
            system_prompt="system",
            user_prompt="user",
            response_model=DemoResponse,
        )


def _fake_client(
    response: SimpleNamespace | None = None,
    error: Exception | None = None,
) -> SimpleNamespace:
    parse = AsyncMock(side_effect=error) if error else AsyncMock(return_value=response)
    return SimpleNamespace(responses=SimpleNamespace(parse=parse))

