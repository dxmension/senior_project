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
    "section": ["section", "section #", "sec", "sec #", "s/t"],
    "avg_gpa": ["avg gpa", "ave gpa", "gpa", "average gpa", "avg. gpa", "mean gpa", "avggpa"],
    "total": ["total", "# gpa grades", "# letter grades", "n", "enrolled", "total enrolled", "count", "enr"],
}


@dataclass
class GpaStatEntry:
    code: str
    level: str
    section: str | None
    avg_gpa: float | None
    total_enrolled: int | None
    grade_distribution: dict[str, float] = field(default_factory=dict)


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


_TABLE_STRATEGIES = [
    {},  # pdfplumber default (line-based)
    {"vertical_strategy": "lines_strict", "horizontal_strategy": "lines_strict"},
    {"vertical_strategy": "text", "horizontal_strategy": "text"},
]

# Grade columns in the order they appear in the Section E tables.
_SECTION_E_GRADE_COLS = ["A", "B", "C", "D", "F", "P", "I", "AU", "W"]


def _parse(file_obj: io.BytesIO) -> tuple[list[GpaStatEntry], list[dict]]:
    entries: list[GpaStatEntry] = []
    errors: list[dict] = []

    raw = file_obj.read()

    # Try table-extraction strategies first.
    for strategy in _TABLE_STRATEGIES:
        had_headerless = False
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                for table in (page.extract_tables(strategy) or []):
                    if not table or len(table) < 2:
                        continue
                    pe, er, skipped = _process_table(table, page_num)
                    if skipped:
                        had_headerless = True
                    entries.extend(pe)
                    errors.extend(er)

        # Only treat as a complete result if no tables were skipped due to missing
        # headers.  A skipped table means the PDF has multi-page tables where only
        # the first page carries the header row — table extraction is therefore
        # partial and we must fall through to the text-line fallback instead.
        if entries and any(e.grade_distribution for e in entries) and not had_headerless:
            logger.debug(
                "GPA PDF parsed with strategy %s, got %d entries with grade data.",
                strategy or "default", len(entries),
            )
            return entries, errors

        if entries:
            logger.debug(
                "GPA PDF strategy %s found %d entries but no grade distribution data, trying next.",
                strategy or "default", len(entries),
            )
        else:
            logger.debug("GPA PDF strategy %s yielded no entries, trying next.", strategy or "default")
        entries = []
        errors = []

    # Final fallback: parse directly from extracted text lines.
    # This handles PDFs where pdfplumber cannot detect table borders, or where
    # table extraction finds rows but misses the grade-percentage columns.
    logger.debug("GPA PDF: falling back to text-line parsing.")
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            pe, er = _parse_text_lines(text, page_num)
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
    """Return the index of the row most likely to be the header, or -1 if not found."""
    hints = {"gpa", "grade", "enrolled", "course", "section", "total"}
    for i, row in enumerate(table[:6]):
        text = " ".join(_norm(c) for c in row)
        if sum(1 for h in hints if h in text) >= 2:
            return i
    return -1


def _process_table(
    table: list[list], page_num: int
) -> tuple[list[GpaStatEntry], list[dict], bool]:
    """Process one extracted table.  Returns (entries, errors, skipped_no_header)."""
    header_idx = _find_header_row(table)
    if header_idx == -1:
        # Continuation page — no recognisable header row, skip.
        return [], [], True

    headers = [str(c or "").strip() for c in table[header_idx]]
    data_rows = table[header_idx + 1 :]

    if not data_rows:
        return [], [], False

    df = pd.DataFrame(data_rows, columns=headers)
    df = df.where(pd.notnull(df), None)

    course_col = _find_col(df, _GPA_COL_ALIASES["course"])
    section_col = _find_col(df, _GPA_COL_ALIASES["section"])
    avg_gpa_col = _find_col(df, _GPA_COL_ALIASES["avg_gpa"])
    total_col = _find_col(df, _GPA_COL_ALIASES["total"])

    # Identify grade columns by matching header to known grade letters.
    # The PDF prefixes columns with "%" (e.g. "%A", "%B"), so strip it before matching.
    grade_cols: dict[str, str] = {}
    for col in df.columns:
        upper = str(col).strip().upper().lstrip("%")
        if upper in GRADE_LETTERS:
            grade_cols[upper] = col

    logger.debug(
        "Page %s table: headers=%s | course_col=%s | section_col=%s | "
        "avg_gpa_col=%s | total_col=%s | grade_cols=%s",
        page_num, list(df.columns), course_col, section_col,
        avg_gpa_col, total_col, grade_cols,
    )

    # Need at least a course column OR some grade columns to be a stats table
    if not course_col and not grade_cols:
        return [], [], False

    entries: list[GpaStatEntry] = []
    errors: list[dict] = []

    for row_idx, row in df.iterrows():
        try:
            entry = _parse_row(row, course_col, section_col, avg_gpa_col, total_col, grade_cols)
            if entry:
                entries.append(entry)
        except Exception as exc:
            errors.append({"row": int(row_idx) + header_idx + 1, "page": page_num, "error": str(exc)})

    return entries, errors, False


def _get_val(row: pd.Series, col: str) -> str:
    """Safely extract a scalar string from a row, handling duplicate-column Series."""
    val = row.get(col)
    if isinstance(val, pd.Series):
        val = val.iloc[0] if not val.empty else None
    if val is None:
        return ""
    try:
        if pd.isna(val):
            return ""
    except (TypeError, ValueError):
        pass
    return str(val).strip()


def _parse_row(
    row: pd.Series,
    course_col: str | None,
    section_col: str | None,
    avg_gpa_col: str | None,
    total_col: str | None,
    grade_cols: dict[str, str],
) -> GpaStatEntry | None:
    raw_course = _get_val(row, course_col) if course_col else ""
    if not raw_course:
        return None

    m = CODE_LEVEL_RE.search(raw_course)
    if not m:
        return None

    code = m.group(1).upper()
    level = m.group(2)

    section: str | None = None
    if section_col:
        raw_sec = _get_val(row, section_col)
        section = raw_sec or None

    avg_gpa: float | None = None
    if avg_gpa_col:
        try:
            val = _get_val(row, avg_gpa_col)
            avg_gpa = float(val) if val else None
        except ValueError:
            pass

    total_enrolled: int | None = None
    if total_col:
        try:
            val = _get_val(row, total_col)
            total_enrolled = int(float(val)) if val else None
        except ValueError:
            pass

    grade_distribution: dict[str, float] = {}
    for letter, col_name in grade_cols.items():
        try:
            val = _get_val(row, col_name).rstrip("%")
            pct = float(val) if val else 0.0
            if pct > 0:
                grade_distribution[letter] = pct
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


def _is_num(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def _parse_text_lines(text: str, page_num: int) -> tuple[list[GpaStatEntry], list[dict]]:
    """
    Parse GPA data from raw extracted text when table detection fails.

    Each data row in the Section E tables looks like (on one text line):
      CHME 200 Basic Principles ... 1 30 3.09 0.95 3.33 43.3 40.0 6.7 6.7 3.3 0.0 0.0 0.0 0.0 30

    After the course code the remaining numeric tokens are (in order):
      [level_number?]  section  gpa_count  avg_gpa  sd  median_gpa
      %A  %B  %C  %D  %F  %P  %I  %AU  %W  letter_count
    """
    entries: list[GpaStatEntry] = []
    errors: list[dict] = []

    logger.debug("Text-line fallback: page %s has %d lines.", page_num, len(text.splitlines()))

    for line in text.splitlines():
        tokens = line.split()
        if not tokens:
            continue

        # Identify course code in the first one or two tokens.
        m = CODE_LEVEL_RE.match(tokens[0])
        if not m and len(tokens) > 1:
            m = CODE_LEVEL_RE.match(tokens[0] + tokens[1])
        if not m:
            continue

        code = m.group(1).upper()
        level = m.group(2)

        # Collect all numeric tokens from the full line.
        numerics = [float(t) for t in tokens if _is_num(t)]

        # If the course level number appears as the first numeric, skip it
        # (e.g. "CHME 200 ..." → "200" is numeric but is the course number).
        try:
            level_num = float(re.sub(r"[A-Z]", "", level))
            if numerics and numerics[0] == level_num:
                numerics = numerics[1:]
        except ValueError:
            pass

        # Need at least: section + gpa_count + avg_gpa + sd + median + 1 grade = 6
        if len(numerics) < 6:
            continue

        try:
            idx = 0
            section = str(int(numerics[idx])); idx += 1
            total_enrolled = int(numerics[idx]); idx += 1
            avg_gpa = numerics[idx]; idx += 1
            idx += 1  # SD — not stored
            idx += 1  # Median GPA — not stored

            grade_distribution: dict[str, float] = {}
            # Consume one value per grade column, leaving the last numeric
            # for letter_count.
            remaining_after_grades = len(_SECTION_E_GRADE_COLS)
            for grade in _SECTION_E_GRADE_COLS:
                if idx + remaining_after_grades <= len(numerics):
                    pct = numerics[idx]; idx += 1
                    if pct > 0:
                        grade_distribution[grade] = pct
                remaining_after_grades -= 1

            entries.append(GpaStatEntry(
                code=code,
                level=level,
                section=section,
                avg_gpa=avg_gpa,
                total_enrolled=total_enrolled,
                grade_distribution=grade_distribution,
            ))
        except (IndexError, ValueError) as exc:
            errors.append({"page": page_num, "line": line[:80], "error": str(exc)})

    return entries, errors