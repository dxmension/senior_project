"""
Handbook parsing service.

Flow:
  1. Receive PDF bytes + enrollment year.
  2. Create HandbookPlan row with status="processing".
  3. Extract text from PDF with pdfplumber.
  4. Send text (chunked if needed) to OpenAI and ask it to return
     a JSON plan matching our audit DegreePlan structure.
  5. Validate JSON + store → status="completed".
  6. On any error → status="failed" with error message.
"""
from __future__ import annotations

import io
import json
import logging
import re
import textwrap
from typing import Any

import pdfplumber
from openai import AsyncOpenAI
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.config import settings
from nutrack.handbook.models import HandbookPlan
from nutrack.handbook.schemas import HandbookStatusResponse, HandbookUploadResponse

logger = logging.getLogger(__name__)

# Maximum characters sent to OpenAI in one call.  GPT-4o supports ~120 k tokens
# (≈ 90 k chars).  We stay well under to leave room for the system prompt.
_MAX_CHARS = 80_000

_SYSTEM_PROMPT = textwrap.dedent("""\
You are an academic-requirements parser for Nazarbaev University.
You will receive the extracted text of an undergraduate academic handbook.

Your task is to return ONLY a valid JSON object (no markdown, no explanation)
with the following structure:

{
  "<major_key>": {
    "total_ects": <int>,
    "categories": [
      {
        "name": "<category name>",
        "requirements": [
          {
            "name": "<requirement display name>",
            "patterns": ["<COURSE CODE>", ...],
            "required_count": <int>,
            "ects_per_course": <int>,
            "is_elective": <bool>,
            "note": "<optional short note>"
          }
        ]
      }
    ]
  }
}

Rules:
- major_key must be the major name in lowercase, e.g. "computer science".
- patterns are course codes like "CSCI 151" for a specific course, or
  "CSCI 3" for any CSCI 300-level course, or "CSCI" for any CSCI course.
- required_count is how many distinct courses from this requirement must be taken.
- is_elective is true when the requirement is an elective pool (students choose N
  from a set), false when specific courses are required.
- Courses that are required (is_elective=false) must NOT appear in any elective
  pool (is_elective=true) for the same major — each course is counted only once.
- ects_per_course defaults to 6 if not specified.
- Include ALL undergraduate programs found in the handbook.
- Use exact course codes as they appear in the text (e.g., "CSCI 151").
- For elective pools where ANY course from a department qualifies, use the dept
  prefix as the pattern (e.g., "CSCI 3" for any 300-level CS elective).
""")


def _extract_text(pdf_bytes: bytes) -> str:
    """Extract all text from PDF, tables first then prose, per page."""
    parts: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            for table in (page.extract_tables() or []):
                for row in table:
                    if row:
                        parts.append(" | ".join(str(c or "").strip() for c in row))
            text = page.extract_text()
            if text:
                parts.append(text)
    return "\n".join(parts)


def _truncate(text: str, max_chars: int = _MAX_CHARS) -> str:
    if len(text) <= max_chars:
        return text
    # Keep the first portion (university core + first majors) and the last
    # portion (remaining majors).  Middle material is often boilerplate.
    half = max_chars // 2
    return text[:half] + "\n...[truncated]...\n" + text[-half:]


def _validate_plans(data: Any) -> dict[str, Any]:
    """
    Light validation: confirm it's a dict of major → {total_ects, categories}.
    Raises ValueError on obvious structural problems.
    """
    if not isinstance(data, dict):
        raise ValueError("Top-level JSON must be an object")
    for major, plan in data.items():
        if not isinstance(plan, dict):
            raise ValueError(f"Plan for '{major}' must be an object")
        if "categories" not in plan:
            raise ValueError(f"Plan for '{major}' missing 'categories'")
        for cat in plan["categories"]:
            for req in cat.get("requirements", []):
                if "patterns" not in req:
                    raise ValueError(f"Requirement in '{major}' missing 'patterns'")
    return data


def _classify_category(name: str) -> str:
    """
    Map any category name from the uploaded JSON to one of three canonical buckets.
    """
    n = name.lower()
    if "university" in n or ("core" in n and "major" not in n and "elective" not in n):
        return "University Core"
    if "major" in n:
        return "Major Core"
    return "Electives"


def _normalize_plans(raw: dict[str, Any]) -> dict[str, Any]:
    """
    Normalize an uploaded JSON file to the internal audit format.

    Handles:
    - Optional top-level school wrapper ({"SEDS": {...}} or {"SSH": {...}})
    - Underscore major keys  →  space-separated  (computer_science → computer science)
    - required_count "all_required" / "remaining_credits"  →  requirement skipped
    - Pattern "ANY"  →  "*"
    - All categories consolidated into: University Core | Major Core | Electives
    """
    def _looks_like_wrapper(d: dict) -> bool:
        return all(
            isinstance(v, dict) and not v.get("categories")
            for v in d.values()
        )

    if _looks_like_wrapper(raw):
        merged: dict[str, Any] = {}
        for school_data in raw.values():
            if isinstance(school_data, dict):
                merged.update(school_data)
        raw = merged

    normalized: dict[str, Any] = {}
    for major_key, plan_data in raw.items():
        clean_key = major_key.replace("_", " ").strip().lower()

        # Bucket requirements into the three canonical categories
        buckets: dict[str, list[dict]] = {
            "University Core": [],
            "Major Core": [],
            "Electives": [],
        }

        for cat in plan_data.get("categories", []):
            cat_bucket = _classify_category(cat.get("name", ""))

            for req in cat.get("requirements", []):
                rc = req.get("required_count", 1)
                if rc == "all_required":
                    continue  # can't track without explicit course list
                if rc == "remaining_credits":
                    rc = 2  # show as 2 open elective slots
                patterns = [
                    "*" if p == "ANY" else p
                    for p in req.get("patterns", [])
                ]
                req_name = req.get("name", "")
                # Requirements whose name contains "elective" always go to Electives,
                # regardless of which category they appear in the source JSON.
                is_elective_req = (
                    bool(req.get("is_elective", False))
                    or "elective" in req_name.lower()
                )
                bucket = "Electives" if is_elective_req else cat_bucket

                buckets[bucket].append({
                    "name": req_name,
                    "patterns": patterns,
                    "required_count": int(rc),
                    "ects_per_course": int(req.get("ects_per_course", 6)),
                    "is_elective": is_elective_req,
                    "note": req.get("note", ""),
                })

        categories = [
            {"name": name, "requirements": reqs}
            for name, reqs in buckets.items()
            if reqs
        ]

        normalized[clean_key] = {
            "total_ects": int(plan_data.get("total_ects", 240)),
            "categories": categories,
        }

    return normalized


class HandbookService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def upload_and_parse(
        self,
        enrollment_year: int,
        filename: str,
        pdf_bytes: bytes,
    ) -> HandbookUploadResponse:
        """
        Upsert a HandbookPlan row, parse the PDF, store result.
        If a plan already exists for that year, it is replaced.
        """
        # Upsert: delete existing if any, then create fresh
        existing = await self._get_by_year(enrollment_year)
        if existing:
            await self.session.delete(existing)
            await self.session.flush()

        plan = HandbookPlan(
            enrollment_year=enrollment_year,
            filename=filename,
            status="processing",
        )
        self.session.add(plan)
        await self.session.flush()  # get plan.id

        try:
            raw_text = _extract_text(pdf_bytes)
            truncated = _truncate(raw_text)
            plans_json = await self._parse_with_openai(truncated)
            plan.plans = plans_json
            plan.status = "completed"
            plan.error = None
        except Exception as exc:
            logger.exception("Handbook parse failed for year %d", enrollment_year)
            plan.status = "failed"
            plan.error = str(exc)

        await self.session.commit()
        await self.session.refresh(plan)
        return HandbookUploadResponse(
            id=plan.id,
            enrollment_year=plan.enrollment_year,
            filename=plan.filename,
            status=plan.status,
            error=plan.error,
            created_at=plan.created_at,
        )

    async def upload_json(
        self,
        enrollment_year: int,
        filename: str,
        json_bytes: bytes,
    ) -> HandbookUploadResponse:
        """
        Upsert a HandbookPlan from a JSON file (no OpenAI needed).
        The JSON is normalized and stored directly.
        """
        existing = await self._get_by_year(enrollment_year)
        prior_plans: dict[str, Any] = {}
        if existing:
            prior_plans = existing.plans or {}
            await self.session.delete(existing)
            await self.session.flush()

        plan = HandbookPlan(
            enrollment_year=enrollment_year,
            filename=filename,
            status="processing",
        )
        self.session.add(plan)
        await self.session.flush()

        try:
            raw = json.loads(json_bytes.decode("utf-8"))
            new_plans = _normalize_plans(raw)
            _validate_plans(new_plans)
            # Merge with previously uploaded plans for this year (SEDS + SSH)
            merged = {**prior_plans, **new_plans}
            plan.plans = merged
            plan.status = "completed"
            plan.error = None
        except Exception as exc:
            logger.exception("Handbook JSON parse failed for year %d", enrollment_year)
            plan.status = "failed"
            plan.error = str(exc)

        await self.session.commit()
        await self.session.refresh(plan)
        return HandbookUploadResponse(
            id=plan.id,
            enrollment_year=plan.enrollment_year,
            filename=plan.filename,
            status=plan.status,
            error=plan.error,
            created_at=plan.created_at,
        )

    async def get_status(self, enrollment_year: int) -> HandbookStatusResponse | None:
        plan = await self._get_by_year(enrollment_year)
        if not plan:
            return None
        majors = list(plan.plans.keys()) if plan.plans else []
        return HandbookStatusResponse(
            id=plan.id,
            enrollment_year=plan.enrollment_year,
            filename=plan.filename,
            status=plan.status,
            majors_parsed=majors,
            error=plan.error,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )

    async def get_plans_for_year(self, enrollment_year: int) -> dict[str, Any] | None:
        """Return raw plans JSON for a given enrollment year, or None."""
        plan = await self._get_by_year(enrollment_year)
        if plan and plan.status == "completed" and plan.plans:
            return plan.plans
        return None

    async def _get_by_year(self, year: int) -> HandbookPlan | None:
        result = await self.session.execute(
            select(HandbookPlan).where(HandbookPlan.enrollment_year == year)
        )
        return result.scalar_one_or_none()

    async def _parse_with_openai(self, text: str) -> dict[str, Any]:
        response = await self._openai.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            temperature=0,
            max_tokens=16_000,
        )
        content = response.choices[0].message.content or "{}"
        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(f"OpenAI returned invalid JSON: {exc}") from exc
        return _validate_plans(data)
