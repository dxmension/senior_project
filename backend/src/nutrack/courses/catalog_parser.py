"""
Course catalog parser — Excel (.xlsx, .xls) and CSV.

Distinct from parser.py (semester schedule PDF):
  - This handles the persistent course catalog: what courses exist,
    their descriptions, prerequisites, school, ECTS.
  - The schedule parser handles what is being offered this term.

NU publishes their course catalog as Excel/CSV.  This parser handles
both formats via a common pandas read path, then maps to CourseCatalogEntity.
"""
import logging
import re
from io import BytesIO

import pandas as pd
from pydantic import ValidationError

from nutrack.courses.domain import CourseEntity

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Column aliases
# ---------------------------------------------------------------------------

CATALOG_COLUMN_MAP: dict[str, list[str]] = {
    "code": ["code", "course code", "course abbr", "course abbreviation", "courseabbr"],
    "level": ["level", "course level", "number", "course number"],
    "title": ["title", "course title", "name", "course name", "coursetitle"],
    "ects": ["ects", "credits ects", "cr ects", "cr(ects)", "credits"],
    "credits_us": ["us credits", "credits us", "cr us", "cr(us)"],
    "description": ["description", "course description", "desc"],
    "prerequisites": ["prerequisites", "prereq", "pre-req", "prerequisite", "prereqs"],
    "school": ["school", "faculty", "college"],
    "department": ["department", "dept", "program"],
    "academic_level": ["academic level", "level type", "ug gr", "ug/gr", "degree level"],
    "pass_grade": ["pass grade", "minimum grade", "min grade", "passing grade"],
}

CODE_PATTERN = re.compile(r"([A-Z]{2,})[\s,;:/-]*([0-9]{2,4}[A-Z]?)")

SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def parse_catalog(
    contents: bytes,
    filename: str,
) -> tuple[list[CourseEntity], list[dict[str, object]]]:
    """
    Parse a course catalog from raw file bytes.

    Returns:
        (entities, errors) where entities are valid CourseEntity objects
        and errors are row-level dicts with {row, course_code, error}.

    Raises:
        ValueError: if the file format is unsupported or unreadable.
    """
    ext = _get_extension(filename)
    df = _read_dataframe(contents, ext)
    df = _normalize_columns(df)
    df = df.where(pd.notnull(df), None)

    code_col = _require_col(df, "code")
    title_col = _require_col(df, "title")
    ects_col = _require_col(df, "ects")
    optional = _map_optional_cols(df)

    entities, errors = _build_entities(df, code_col, title_col, ects_col, optional)

    logger.info(
        "Course catalog parsed.",
        extra={
            "filename": filename,
            "rows_total": len(df),
            "parsed_ok": len(entities),
            "errors": len(errors),
        },
    )
    return entities, errors


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------


def _get_extension(filename: str) -> str:
    name = (filename or "").lower().strip()
    for ext in SUPPORTED_EXTENSIONS:
        if name.endswith(ext):
            return ext
    raise ValueError(
        f"Unsupported file type '{filename}'. "
        f"Accepted: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
    )


def _read_dataframe(contents: bytes, ext: str) -> pd.DataFrame:
    try:
        if ext == ".csv":
            return pd.read_csv(BytesIO(contents), dtype=str)
        return pd.read_excel(BytesIO(contents), dtype=str)
    except Exception as exc:
        raise ValueError(f"Failed to read file: {exc}") from exc


# ---------------------------------------------------------------------------
# Column resolution
# ---------------------------------------------------------------------------


def _simplify(text: str | None) -> str:
    if not text:
        return ""
    s = str(text).lower().strip()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename raw column names to normalised form for lookup."""
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _find_col(df: pd.DataFrame, key: str) -> str | None:
    """Return the actual DataFrame column name matching the canonical key."""
    aliases = {_simplify(a) for a in CATALOG_COLUMN_MAP[key]}
    for col in df.columns:
        if _simplify(col) in aliases:
            return col
    return None


def _require_col(df: pd.DataFrame, key: str) -> str:
    col = _find_col(df, key)
    if not col:
        raise ValueError(
            f"Required column '{key}' not found. "
            f"Expected one of: {CATALOG_COLUMN_MAP[key]}. "
            f"Found columns: {list(df.columns)}"
        )
    return col


def _map_optional_cols(df: pd.DataFrame) -> dict[str, str | None]:
    keys = [
        "level",
        "credits_us",
        "description",
        "prerequisites",
        "school",
        "department",
        "academic_level",
        "pass_grade",
    ]
    return {k: _find_col(df, k) for k in keys}


# ---------------------------------------------------------------------------
# Row processing
# ---------------------------------------------------------------------------


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _to_int(value: object) -> int | None:
    text = _as_text(value).replace(",", ".")
    if not text:
        return None
    try:
        return int(float(text))
    except (ValueError, TypeError):
        match = re.search(r"\d+(?:\.\d+)?", text)
        return int(float(match.group(0))) if match else None


def _to_float(value: object) -> float | None:
    text = _as_text(value)
    if not text:
        return None
    try:
        return float(text)
    except (ValueError, TypeError):
        return None


def _parse_code_level(raw: str) -> tuple[str, str]:
    """
    Split raw code string into (code_prefix, level_number).

    "CSCI 151"   → ("CSCI", "151")
    "MATH161"    → ("MATH", "161")
    "CSCI"       → ("CSCI", "")
    """
    text = re.sub(r"\s+", " ", raw.upper().strip())
    m = CODE_PATTERN.search(text)
    if m:
        return m.group(1), m.group(2)
    fallback = re.match(r"([A-Z]{2,})", text)
    if fallback:
        return fallback.group(1), ""
    return text, ""


def _col_text(row: pd.Series, col: str | None) -> str | None:
    if not col:
        return None
    val = _as_text(row.get(col))
    return val or None


def _build_entity(
    row: pd.Series,
    code: str,
    level: str,
    title: str,
    ects: int,
    optional: dict[str, str | None],
) -> CourseEntity:
    # Level: prefer dedicated level column, fall back to parsed level
    level_col = optional.get("level")
    row_level = _as_text(row.get(level_col)) if level_col else ""
    resolved_level = row_level.upper().strip() or level

    credits_us_col = optional.get("credits_us")

    try:
        return CourseEntity(
            code=code,
            title=title,
            level=resolved_level,
            ects=ects,
            department=_col_text(row, optional.get("department")),
            description=_col_text(row, optional.get("description")),
            school=_col_text(row, optional.get("school")),
            academic_level=_col_text(row, optional.get("academic_level")),
            credits_us=_to_float(row.get(credits_us_col) if credits_us_col else None),
            # catalog-only fields (passed through domain entity)
            section=None,
            start_date=None,
            end_date=None,
            days=None,
            meeting_time=None,
            enrolled=None,
            capacity=None,
            faculty=None,
            room=None,
        )
    except ValidationError as exc:
        first = exc.errors()[0]
        raise ValueError(first.get("msg", "Invalid row")) from exc


def _parse_row(
    row: pd.Series,
    code_col: str,
    title_col: str,
    ects_col: str,
    optional: dict[str, str | None],
) -> CourseEntity | None:
    raw_code = _as_text(row.get(code_col))
    title = _as_text(row.get(title_col))
    ects = _to_int(row.get(ects_col))

    # Skip fully blank rows
    if not raw_code and not title and ects is None:
        return None

    if not raw_code:
        raise ValueError("Missing course code.")
    if not title:
        raise ValueError("Missing course title.")
    if ects is None:
        raise ValueError("Invalid ECTS value.")

    code, level = _parse_code_level(raw_code)
    if not level:
        # Try to get level from dedicated column
        level_col = optional.get("level")
        level = _as_text(row.get(level_col)).upper().strip() if level_col else ""
    if not level:
        raise ValueError("Cannot determine course level.")

    return _build_entity(row, code, level, title, ects, optional)


def _build_entities(
    df: pd.DataFrame,
    code_col: str,
    title_col: str,
    ects_col: str,
    optional: dict[str, str | None],
) -> tuple[list[CourseEntity], list[dict[str, object]]]:
    entities: list[CourseEntity] = []
    errors: list[dict[str, object]] = []

    for idx, row in df.iterrows():
        try:
            entity = _parse_row(row, code_col, title_col, ects_col, optional)
        except ValueError as exc:
            errors.append(
                {
                    "row": int(idx) + 2,  # +2: 1-indexed + header row
                    "course_code": _as_text(row.get(code_col)) or None,
                    "course_title": _as_text(row.get(title_col)) or None,
                    "error": str(exc),
                }
            )
            logger.warning(
                "Invalid catalog row skipped.",
                extra={
                    "row": idx + 2,
                    "code": _as_text(row.get(code_col)),
                    "error": str(exc),
                },
            )
            continue

        if entity:
            entities.append(entity)

    return entities, errors
