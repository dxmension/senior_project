"""
Parser for NU GPA statistics PDF reports.

Expected format — a table per page with columns:
  Course (e.g. "CSCI 151"), Section, Avg GPA, Total Enrolled,
  followed by grade columns: A, A-, B+, B, B-, C+, C, C-, D+, D, F, W, I, …

Returns:
  (list[GpaStatEntry], list[dict])  — valid entries + per-row parse errors.
"""
from __future__ import annotations

import io
import logging
import re
from dataclasses import dataclass, field

import pandas as pd
import pdfplumber

logger = logging.getLogger(__name__)

GRADE_LETTERS = {"A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D", "F", "W", "I", "AU", "P", "NP"}
CODE_LEVEL_RE = re.compile(r"([A-Z]{2,})\s*([0-9]{2,4}[A-Z]?)")

_GPA_COL_ALIASES = {
    "course": ["course", "code", "course code", "course abbr", "courseabbr"],
    "section": ["section", "sec", "s/t"],
    "avg_gpa": ["avg gpa", "gpa", "average gpa", "avg. gpa", "mean gpa", "avggpa"],
    "total": ["total", "n", "enrolled", "total enrolled", "count", "enr"],
}


@dataclass
class GpaStatEntry:
    code: str
    level: str
    section: str | None
    avg_gpa: float | None
    total_enrolled: int | None
    grade_distribution: dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_gpa_stats(contents: bytes, filename: str) -> tuple[list[GpaStatEntry], list[dict]]:
    """Parse a GPA statistics PDF and return (entries, errors)."""
    try:
        return _parse(io.BytesIO(contents))
    except Exception as exc:
        raise ValueError(f"Failed to parse GPA stats PDF '{filename}': {exc}") from exc


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _parse(file_obj: io.BytesIO) -> tuple[list[GpaStatEntry], list[dict]]:
    entries: list[GpaStatEntry] = []
    errors: list[dict] = []

    with pdfplumber.open(file_obj) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            for table in (page.extract_tables() or []):
                if not table or len(table) < 2:
                    continue
                pe, er = _process_table(table, page_num)
                entries.extend(pe)
                errors.extend(er)

    return entries, errors


def _norm(s: object) -> str:
    return re.sub(r"\s+", " ", str(s or "")).strip().lower()


def _find_col(df: pd.DataFrame, aliases: list[str]) -> str | None:
    normed = {_norm(c): c for c in df.columns}
    for alias in aliases:
        if alias in normed:
            return normed[alias]
    return None


def _find_header_row(table: list[list]) -> int:
    """Return the index of the row most likely to be the header."""
    hints = {"gpa", "grade", "enrolled", "course", "section", "total"}
    for i, row in enumerate(table[:6]):
        text = " ".join(_norm(c) for c in row)
        if sum(1 for h in hints if h in text) >= 2:
            return i
    return 0


def _process_table(
    table: list[list], page_num: int
) -> tuple[list[GpaStatEntry], list[dict]]:
    header_idx = _find_header_row(table)
    headers = [str(c or "").strip() for c in table[header_idx]]
    data_rows = table[header_idx + 1 :]

    if not data_rows:
        return [], []

    df = pd.DataFrame(data_rows, columns=headers)
    df = df.where(pd.notnull(df), None)

    course_col = _find_col(df, _GPA_COL_ALIASES["course"])
    section_col = _find_col(df, _GPA_COL_ALIASES["section"])
    avg_gpa_col = _find_col(df, _GPA_COL_ALIASES["avg_gpa"])
    total_col = _find_col(df, _GPA_COL_ALIASES["total"])

    # Identify grade columns by matching header to known grade letters
    grade_cols: dict[str, str] = {}
    for col in df.columns:
        upper = str(col).strip().upper()
        if upper in GRADE_LETTERS:
            grade_cols[upper] = col

    # Need at least a course column OR some grade columns to be a stats table
    if not course_col and not grade_cols:
        return [], []

    entries: list[GpaStatEntry] = []
    errors: list[dict] = []

    for row_idx, row in df.iterrows():
        try:
            entry = _parse_row(row, course_col, section_col, avg_gpa_col, total_col, grade_cols)
            if entry:
                entries.append(entry)
        except Exception as exc:
            errors.append({"row": int(row_idx) + header_idx + 1, "page": page_num, "error": str(exc)})

    return entries, errors


def _parse_row(
    row: pd.Series,
    course_col: str | None,
    section_col: str | None,
    avg_gpa_col: str | None,
    total_col: str | None,
    grade_cols: dict[str, str],
) -> GpaStatEntry | None:
    raw_course = str(row.get(course_col, "") or "").strip() if course_col else ""
    if not raw_course:
        return None

    m = CODE_LEVEL_RE.search(raw_course)
    if not m:
        return None

    code = m.group(1).upper()
    level = m.group(2)

    section: str | None = None
    if section_col:
        raw_sec = str(row.get(section_col, "") or "").strip()
        section = raw_sec or None

    avg_gpa: float | None = None
    if avg_gpa_col:
        try:
            val = str(row.get(avg_gpa_col, "") or "").strip()
            avg_gpa = float(val) if val else None
        except ValueError:
            pass

    total_enrolled: int | None = None
    if total_col:
        try:
            val = str(row.get(total_col, "") or "").strip()
            total_enrolled = int(float(val)) if val else None
        except ValueError:
            pass

    grade_distribution: dict[str, int] = {}
    for letter, col_name in grade_cols.items():
        try:
            val = str(row.get(col_name, "") or "").strip()
            n = int(float(val)) if val else 0
            if n > 0:
                grade_distribution[letter] = n
        except ValueError:
            pass

    return GpaStatEntry(
        code=code,
        level=level,
        section=section,
        avg_gpa=avg_gpa,
        total_enrolled=total_enrolled,
        grade_distribution=grade_distribution,
    )
