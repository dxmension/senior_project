# src/foresee/lib/llm/utils.py
from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import BaseModel


def _snip(text: Any, n: int = 60) -> str:
    if text is None:
        return ""
    s = " ".join(str(text).split())
    return s[:n] + ("…" if len(s) > n else "")


_MISSING = object()


def _resolve_ref(*, root: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Unexpected $ref format: {ref!r}")

    target: Any = root
    for key in ref[2:].split("/"):
        if not isinstance(target, dict) or key not in target:
            raise ValueError(f"Unable to resolve $ref: {ref!r}")
        target = target[key]

    if not isinstance(target, dict):
        raise ValueError(f"Resolved $ref is not an object schema: {ref!r}")
    return target


def _ensure_strict_openai_schema(node: Any, *, root: dict[str, Any]) -> Any:
    """
    Mutate JSON schema to OpenAI strict format:
    - every object property is required
    - optional values remain nullable (from Pydantic anyOf/type null)
    - additionalProperties=false on every object node
    """
    if not isinstance(node, dict):
        return node

    defs = node.get("$defs")
    if isinstance(defs, dict):
        for key, value in list(defs.items()):
            defs[key] = _ensure_strict_openai_schema(value, root=root)

    definitions = node.get("definitions")
    if isinstance(definitions, dict):
        for key, value in list(definitions.items()):
            definitions[key] = _ensure_strict_openai_schema(value, root=root)

    if node.get("type") == "object" and "additionalProperties" not in node:
        node["additionalProperties"] = False

    properties = node.get("properties")
    if isinstance(properties, dict):
        node["required"] = list(properties.keys())
        for key, value in list(properties.items()):
            properties[key] = _ensure_strict_openai_schema(value, root=root)

    items = node.get("items")
    if isinstance(items, dict):
        node["items"] = _ensure_strict_openai_schema(items, root=root)

    any_of = node.get("anyOf")
    if isinstance(any_of, list):
        node["anyOf"] = [_ensure_strict_openai_schema(value, root=root) for value in any_of]

    all_of = node.get("allOf")
    if isinstance(all_of, list):
        if len(all_of) == 1:
            merged = _ensure_strict_openai_schema(all_of[0], root=root)
            node.pop("allOf", None)
            if isinstance(merged, dict):
                node.update(merged)
        else:
            node["allOf"] = [_ensure_strict_openai_schema(value, root=root) for value in all_of]

    # None defaults create noise in strict schemas and are not needed.
    if node.get("default", _MISSING) is None:
        node.pop("default", None)

    # Inline $ref when it is mixed with other keys.
    ref = node.get("$ref")
    if isinstance(ref, str) and len(node) > 1:
        resolved = _resolve_ref(root=root, ref=ref)
        node.update({**resolved, **node})
        node.pop("$ref", None)
        return _ensure_strict_openai_schema(node, root=root)

    return node


@lru_cache(maxsize=128)
def _cached_schema_json(model_cls: type[BaseModel]) -> str:
    """
    Pydantic v2 JSON schema for json_schema response_format.

    OpenAI strict schema requirements:
    - all object fields are required
    - optional values are represented as nullable types
    - additionalProperties=false for object nodes
    """
    if not hasattr(model_cls, "model_json_schema"):
        raise RuntimeError("Unsupported Pydantic version (expected v2)")

    schema = model_cls.model_json_schema()
    _ensure_strict_openai_schema(schema, root=schema)
    return json.dumps(schema, ensure_ascii=False, separators=(",", ":"))


def pydantic_schema_dict(model_cls: type[BaseModel]) -> dict:
    return json.loads(_cached_schema_json(model_cls))


def pydantic_schema_size_bytes(model_cls: type[BaseModel]) -> int:
    return len(_cached_schema_json(model_cls).encode("utf-8"))
