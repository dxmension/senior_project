from __future__ import annotations

from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from nutrack.config import settings
from nutrack.tools.llm.exceptions import (
    LLMConfigurationError,
    LLMIncompleteResponseError,
    LLMRefusalError,
    LLMResponseError,
)

T = TypeVar("T", bound=BaseModel)

_client: AsyncOpenAI | None = None
_client_key: str | None = None


def _get_client() -> AsyncOpenAI:
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        raise LLMConfigurationError("OpenAI API key not configured")
    global _client, _client_key
    if _client is None or _client_key != api_key:
        _client = AsyncOpenAI(api_key=api_key)
        _client_key = api_key
    return _client


def _request_kwargs(
    system_prompt: str,
    user_prompt: str,
    response_model: type[T],
    model: str,
    temperature: float,
    max_output_tokens: int | None,
) -> dict[str, Any]:
    kwargs: dict[str, Any] = {
        "model": model,
        "instructions": system_prompt,
        "input": user_prompt,
        "temperature": temperature,
        "text_format": response_model,
    }
    if max_output_tokens is not None:
        kwargs["max_output_tokens"] = max_output_tokens
    return kwargs


def _value(item: Any, name: str) -> Any:
    if isinstance(item, dict):
        return item.get(name)
    return getattr(item, name, None)


def _extract_refusal(response: Any) -> str | None:
    output_items = _value(response, "output") or []
    for item in output_items:
        content_items = _value(item, "content") or []
        for content in content_items:
            if _value(content, "type") != "refusal":
                continue
            return _value(content, "refusal") or "Request was refused"
    return None


def _extract_incomplete_reason(response: Any) -> str | None:
    details = _value(response, "incomplete_details")
    if details is None:
        return None
    return _value(details, "reason")


def _get_parsed_output(response: Any) -> T:
    parsed = _value(response, "output_parsed")
    if parsed is not None:
        return parsed
    refusal = _extract_refusal(response)
    if refusal:
        raise LLMRefusalError(refusal)
    status = _value(response, "status") or "unknown"
    reason = _extract_incomplete_reason(response)
    detail = f"Structured response incomplete: status={status}"
    if reason:
        detail = f"{detail}, reason={reason}"
    raise LLMIncompleteResponseError(detail)


async def parse_structured_response(
    *,
    system_prompt: str,
    user_prompt: str,
    response_model: type[T],
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
    max_output_tokens: int | None = None,
) -> T:
    client = _get_client()
    kwargs = _request_kwargs(
        system_prompt,
        user_prompt,
        response_model,
        model,
        temperature,
        max_output_tokens,
    )
    try:
        response = await client.responses.parse(**kwargs)
    except Exception as exc:
        raise LLMResponseError(str(exc)) from exc
    return _get_parsed_output(response)
