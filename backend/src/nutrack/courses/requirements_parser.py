"""
Parser for Course Requirements and Registration Priorities PDF.

Expected table columns (case-insensitive, partial match):
  - Abbr / Abbreviation  → course code + level (e.g. "BBA 201" or "HST 273/REL 273")
  - PreRequisite / Pre-Req / Prerequisite
  - CoRequisite / Co-Req / Corequisite
  - AntiRequisite / Anti-Req / Antirequisite
  - Priority 1 / 1st Priority  → departments with registration priority 1
  - Priority 2 / 2nd Priority
  - Priority 3 / 3rd Priority
  - Priority 4 / 4th Priority
"""
from __future__ import annotations

import io
import re
from dataclasses import dataclass

import pdfplumber


@dataclass
class RequirementEntry:
    code: str
    level: str
    prerequisites: str | None = None
    corequisites: str | None = None
    antirequisites: str | None = None
    priority_1: str | None = None
    priority_2: str | None = None
    priority_3: str | None = None
    priority_4: str | None = None


def _parse_abbr(raw: str) -> tuple[str, str] | None:
    """Convert 'BBA 201' or 'HST 273/REL 273' to (code, level).

    For cross-listed courses the first abbreviation is used as the primary.
    Handles cells with embedded newlines by scanning for the first match.
    """
    if not raw:
        return None
    primary = raw.split("/")[0]
    for line in primary.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r"^([A-Za-z]{2,6})\s+(\w+)", line)
        if m:
            return m.group(1).upper(), m.group(2)
    return None


def _clean(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def _find_col(header: list, *keywords: str) -> int | None:
    """Return index of the first header cell containing any of the keywords."""
    for i, cell in enumerate(header):
        if cell is None:
            continue
        low = str(cell).strip().lower()
        for kw in keywords:
            if kw in low:
                return i
    return None


def _find_priority_cols(header: list) -> dict[int, int]:
    """Return {priority_number: col_index} for all priority columns found."""
    result: dict[int, int] = {}
    for i, cell in enumerate(header):
        if cell is None:
            continue
        low = str(cell).strip().lower()
        if "priority" in low:
            m = re.search(r"(\d)", low)
            if m:
                result[int(m.group(1))] = i
    return result


def parse_requirements(
    data: bytes, filename: str
) -> tuple[list[RequirementEntry], list[dict]]:
    """Parse a requirements PDF. Returns (entries, parse_errors).

    Column indices discovered from the first header row are reused on
    subsequent pages that don't repeat the header, so multi-page tables
    are parsed correctly.
    """
    entries: list[RequirementEntry] = []
    errors: list[dict] = []

    # Persisted column positions across pages (set once we see a header row)
    abbr_col: int | None = None
    prereq_col: int | None = None
    coreq_col: int | None = None
    antireq_col: int | None = None
    priority_cols: dict[int, int] = {}

    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for table in tables:
                if not table or len(table) < 1:
                    continue

                # Check whether this table has a header row
                header_idx: int | None = None
                for i, row in enumerate(table):
                    if row and any(
                        cell and "abbr" in str(cell).lower() for cell in row
                    ):
                        header_idx = i
                        break

                if header_idx is not None:
                    # Update persisted column indices from this header
                    header = table[header_idx]
                    abbr_col = _find_col(header, "abbr", "abbreviation")
                    prereq_col = _find_col(header, "prerequisite", "pre-req", "prereq")
                    coreq_col = _find_col(header, "corequisite", "co-req", "coreq")
                    antireq_col = _find_col(header, "antirequisite", "anti-req", "antireq")
                    priority_cols = _find_priority_cols(header)
                    data_rows = table[header_idx + 1:]
                else:
                    # No header on this page — reuse previously found column indices
                    if abbr_col is None:
                        # Haven't found a header yet; skip
                        continue
                    data_rows = table

                for row_num, row in enumerate(data_rows, start=1):
                    if not row or len(row) <= abbr_col:
                        continue
                    raw_abbr = _clean(row[abbr_col])
                    if not raw_abbr:
                        continue

                    parsed = _parse_abbr(raw_abbr)
                    if not parsed:
                        errors.append(
                            {
                                "row": row_num,
                                "page": page_num,
                                "error": f"Cannot parse abbreviation: {raw_abbr!r}",
                            }
                        )
                        continue

                    code, level = parsed

                    def _get(col: int | None, _row: list = row) -> str | None:
                        if col is None or len(_row) <= col:
                            return None
                        return _clean(_row[col])

                    entries.append(
                        RequirementEntry(
                            code=code,
                            level=level,
                            prerequisites=_get(prereq_col),
                            corequisites=_get(coreq_col),
                            antirequisites=_get(antireq_col),
                            priority_1=_get(priority_cols.get(1)),
                            priority_2=_get(priority_cols.get(2)),
                            priority_3=_get(priority_cols.get(3)),
                            priority_4=_get(priority_cols.get(4)),
                        )
                    )

    return entries, errors
