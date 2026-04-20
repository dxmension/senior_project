from __future__ import annotations

import json
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
        "text_format": response_model,
    }
    if _supports_temperature(model):
        kwargs["temperature"] = temperature
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


async def run_tool_conversation(
    *,
    system_prompt: str,
    user_prompt: str,
    tools: list[dict[str, Any]],
    tool_handler,
    model: str = "gpt-4o-mini",
    temperature: float = 0.2,
    max_output_tokens: int | None = None,
    max_rounds: int = 8,
) -> str:
    client = _get_client()
    response = await _create_response(
        client,
        model=model,
        temperature=temperature,
        system_prompt=system_prompt,
        input_value=user_prompt,
        tools=tools,
        max_output_tokens=max_output_tokens,
    )
    for _ in range(max_rounds):
        calls = _extract_tool_calls(response)
        if not calls:
            return _response_text(response)
        outputs = await _tool_outputs(tool_handler, calls)
        response = await _create_response(
            client,
            model=model,
            temperature=temperature,
            system_prompt=system_prompt,
            input_value=outputs,
            tools=tools,
            previous_response_id=_value(response, "id"),
            max_output_tokens=max_output_tokens,
        )
    raise LLMIncompleteResponseError("Structured response incomplete: tool loop exceeded max rounds")


async def _create_response(
    client: AsyncOpenAI,
    *,
    model: str,
    temperature: float,
    system_prompt: str,
    input_value: Any,
    tools: list[dict[str, Any]],
    previous_response_id: str | None = None,
    max_output_tokens: int | None,
):
    kwargs: dict[str, Any] = {
        "model": model,
        "instructions": system_prompt,
        "input": input_value,
        "tools": tools,
    }
    if _supports_temperature(model):
        kwargs["temperature"] = temperature
    if previous_response_id is not None:
        kwargs["previous_response_id"] = previous_response_id
    if max_output_tokens is not None:
        kwargs["max_output_tokens"] = max_output_tokens
    try:
        return await client.responses.create(**kwargs)
    except Exception as exc:
        raise LLMResponseError(str(exc)) from exc


def _extract_tool_calls(response: Any) -> list[dict[str, str]]:
    calls: list[dict[str, str]] = []
    for item in _value(response, "output") or []:
        item_type = _value(item, "type")
        if item_type != "function_call":
            continue
        calls.append(
            {
                "call_id": _value(item, "call_id"),
                "name": _value(item, "name"),
                "arguments": _value(item, "arguments") or "{}",
            }
        )
    return calls


async def _tool_outputs(tool_handler, calls: list[dict[str, str]]) -> list[dict[str, str]]:
    outputs: list[dict[str, str]] = []
    for call in calls:
        arguments = json.loads(call["arguments"])
        result = await tool_handler(call["name"], arguments)
        outputs.append(
            {
                "type": "function_call_output",
                "call_id": call["call_id"],
                "output": json.dumps(result),
            }
        )
    return outputs


def _response_text(response: Any) -> str:
    refusal = _extract_refusal(response)
    if refusal:
        raise LLMRefusalError(refusal)
    text = _value(response, "output_text")
    if isinstance(text, str) and text.strip():
        return text
    status = _value(response, "status") or "unknown"
    reason = _extract_incomplete_reason(response)
    detail = f"Structured response incomplete: status={status}"
    if reason:
        detail = f"{detail}, reason={reason}"
    raise LLMIncompleteResponseError(detail)


def _supports_temperature(model: str) -> bool:
    normalized = model.strip().lower()
    if normalized.startswith("gpt-5.1"):
        return True
    if normalized.startswith("gpt-5"):
        return False
    return True
