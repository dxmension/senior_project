# src/foresee/lib/llm/openai.py
from __future__ import annotations

import logging
import re
import time
from uuid import uuid4
from typing import Any, Dict, Optional, Type, TypeVar

import httpx
from openai import OpenAI
from pydantic import BaseModel

from bpmai.logger_config import get_logger, log_event
from .errors import LLMParseError
from .interface import LLMEngine, LLMResult

T = TypeVar("T", bound=BaseModel)
logger = get_logger("LLM.OpenAI")


def _extract_response_parse_meta(raw_response: Any) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}
    if raw_response is None:
        return meta

    request_id = getattr(raw_response, "request_id", None)
    status_code = getattr(raw_response, "status_code", None)
    if request_id is not None:
        meta["request_id"] = request_id
    if status_code is not None:
        meta["http_status_code"] = status_code

    http_response = getattr(raw_response, "http_response", None)
    if http_response is None:
        return meta

    try:
        payload = http_response.json()
    except Exception:
        return meta

    if not isinstance(payload, dict):
        return meta

    status = payload.get("status")
    if status is not None:
        meta["response_status"] = status

    incomplete_details = payload.get("incomplete_details")
    if isinstance(incomplete_details, dict):
        incomplete_reason = incomplete_details.get("reason")
        if incomplete_reason is not None:
            meta["incomplete_reason"] = incomplete_reason

    output_items = payload.get("output")
    if isinstance(output_items, list):
        meta["output_items"] = len(output_items)
        output_text_chars = 0
        incomplete_messages = 0
        for item in output_items:
            if not isinstance(item, dict):
                continue
            if item.get("status") == "incomplete":
                incomplete_messages += 1
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") != "output_text":
                    continue
                text = block.get("text")
                if isinstance(text, str):
                    output_text_chars += len(text)

        meta["output_text_chars"] = output_text_chars
        meta["incomplete_output_messages"] = incomplete_messages

    return meta


def _extract_validation_error_meta(exc: Exception) -> Dict[str, Any]:
    meta: Dict[str, Any] = {}

    try:
        errors = exc.errors()  # type: ignore[attr-defined]
    except Exception:
        errors = None

    if isinstance(errors, list) and errors:
        first = errors[0]
        if isinstance(first, dict):
            input_value = first.get("input")
            error_type = first.get("type")
            if error_type is not None:
                meta["validation_error_type"] = error_type
            if isinstance(input_value, str):
                meta["validation_input_chars"] = len(input_value)
                meta["validation_input_tail"] = input_value[-240:]

    message = str(exc)
    line_col_match = re.search(r"line\s+(\d+)\s+column\s+(\d+)", message)
    if line_col_match:
        meta["validation_error_line"] = int(line_col_match.group(1))
        meta["validation_error_column"] = int(line_col_match.group(2))

    meta["validation_error_excerpt"] = message[:500]
    return meta


def _parse_error_message(parse_meta: Dict[str, Any]) -> str:
    ordered_keys = (
        "response_status",
        "incomplete_reason",
        "validation_error_type",
        "validation_error_line",
        "validation_error_column",
        "validation_input_chars",
        "output_text_chars",
        "request_id",
    )
    parts = []
    for key in ordered_keys:
        value = parse_meta.get(key)
        if value is not None:
            parts.append(f"{key}={value}")
    if not parts:
        return "LLM structured parse failed"
    return f"LLM structured parse failed ({', '.join(parts)})"


class OpenAIEngine(LLMEngine):
    def __init__(
        self,
        *,
        model: str = "gpt-4.1",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        default_request_kwargs: Optional[Dict[str, Any]] = None,
        # sensible defaults for your workload
        timeout_s: float = 600.0,
        max_retries: int = 0,
    ):
        timeout = httpx.Timeout(
            connect=30.0,
            write=30.0,
            read=timeout_s,
            pool=30.0,
        )
        limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            http_client=httpx.Client(timeout=timeout, limits=limits),
        )

        self.default_model = model
        self.default_temperature = temperature
        self.request_defaults: Dict[str, Any] = dict(default_request_kwargs or {})

        log_event(
            logger,
            logging.DEBUG,
            event="llm.engine_init",
            stage="llm",
            message="OpenAI engine initialized",
            model=self.default_model,
            temperature=float(self.default_temperature),
            timeout_s=timeout_s,
            retries=max_retries,
        )

    @staticmethod
    def _build_input(system_prompt: str, user_prompt: str):
        return [
            {"role": "system", "content": [{"type": "input_text", "text": system_prompt}]},
            {"role": "user", "content": [{"type": "input_text", "text": user_prompt}]},
        ]

    def send(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        response_model: Optional[Type[T]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        timeout: Optional[float] = None,  # per-call override
        label: Optional[str] = None,
        session_id: Optional[str] = None,
        log_fields: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> LLMResult[T]:
        eff_model = model or self.default_model
        eff_temp = self.default_temperature if temperature is None else temperature
        call_id = uuid4().hex[:12]

        req_kwargs = {**self.request_defaults, **kwargs}
        input_messages = self._build_input(system_prompt, user_prompt)

        t0 = time.time()

        sys_chars = len(system_prompt or "")
        user_chars = len(user_prompt or "")
        request_log_fields = dict(log_fields or {})
        log_event(
            logger,
            logging.INFO,
            event="llm.request",
            stage="llm",
            message="LLM request started",
            call_id=call_id,
            session_id=session_id,
            llm_label=label or "-",
            model=eff_model,
            temperature=float(eff_temp),
            chars_system=sys_chars,
            chars_user=user_chars,
            **request_log_fields,
        )

        # per-call timeout override via with_options (works reliably with the SDK client)
        client = self.client.with_options(timeout=httpx.Timeout(timeout, connect=10.0)) if timeout else self.client

        try:
            if response_model is not None:
                raw_response = client.responses.with_raw_response.parse(
                    model=eff_model,
                    input=input_messages,
                    temperature=eff_temp,
                    text_format=response_model,
                    **req_kwargs,
                )
                try:
                    response = raw_response.parse()
                    parsed = getattr(response, "output_parsed", None)
                except Exception as parse_exc:
                    dt_ms = round((time.time() - t0) * 1000, 2)
                    parse_meta = {
                        **_extract_response_parse_meta(raw_response),
                        **_extract_validation_error_meta(parse_exc),
                    }
                    log_event(
                        logger,
                        logging.ERROR,
                        event="llm.parse_error",
                        stage="llm",
                        message=_parse_error_message(parse_meta),
                        call_id=call_id,
                        session_id=session_id,
                        llm_label=label or "-",
                        model=eff_model,
                        duration_ms=dt_ms,
                        status="parse_error",
                        **parse_meta,
                        **request_log_fields,
                    )
                    raise
            else:
                response = client.responses.create(
                    model=eff_model,
                    input=input_messages,
                    temperature=eff_temp,
                    **req_kwargs,
                )
                parsed = None
        except Exception:
            dt_ms = round((time.time() - t0) * 1000, 2)
            logger.exception(
                "LLM request failed",
                extra={
                    "event": "llm.error",
                    "stage": "llm",
                    "call_id": call_id,
                    "session_id": session_id,
                    "llm_label": label or "-",
                    "model": eff_model,
                    "duration_ms": dt_ms,
                    "status": "error",
                    **request_log_fields,
                },
            )
            raise

        dt_ms = round((time.time() - t0) * 1000, 2)
        text = getattr(response, "output_text", None)
        usage = getattr(response, "usage", None)

        if response_model is not None and parsed is None:
            raise LLMParseError(
                label=label or "-",
                model=eff_model,
                engine="openai",
                raw_output=text,
                validation_error="output_parsed is None",
            )

        if isinstance(usage, dict):
            usage_input = usage.get("input_tokens")
            usage_output = usage.get("output_tokens")
            usage_total = usage.get("total_tokens")
        else:
            usage_input = getattr(usage, "input_tokens", None) if usage is not None else None
            usage_output = getattr(usage, "output_tokens", None) if usage is not None else None
            usage_total = getattr(usage, "total_tokens", None) if usage is not None else None

        log_event(
            logger,
            logging.INFO,
            event="llm.response",
            stage="llm",
            message="LLM request completed",
            call_id=call_id,
            session_id=session_id,
            llm_label=label or "-",
            model=eff_model,
            duration_ms=dt_ms,
            parsed=bool(parsed) if response_model is not None else False,
            usage_input_tokens=usage_input,
            usage_output_tokens=usage_output,
            usage_total_tokens=usage_total,
            status="ok",
            **request_log_fields,
        )

        return LLMResult(
            engine="openai",
            model=eff_model,
            temperature=eff_temp,
            text=text,
            parsed=parsed,
            usage=usage,
            raw=response,
        )
