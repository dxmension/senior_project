import re
import logging
from datetime import date, datetime

import pandas as pd
import pdfplumber
from pydantic import ValidationError

from nutrack.courses.domain import CourseEntity

logger = logging.getLogger(__name__)

COLUMN_MAP = {
    "code": ["code", "courseabbr", "course abbr", "course code"],
    "level": ["level", "course level"],
    "title": ["title", "course title", "coursetitle"],
    "department": ["department", "dept"],
    "ects": [
        "ects",
        "credits",
        "cr ects",
        "cr ec ts",
        "cr(ects)",
    ],
    "description": ["description", "desc"],
    "school": ["school"],
    "section": ["s/t", "s t", "section"],
    "credits_us": ["cr us", "credits us", "cr(us)", "cr us"],
    "start_date": ["start date", "start"],
    "end_date": ["end date", "end"],
    "days": ["days", "day"],
    "meeting_time": ["time", "class time"],
    "enrolled": ["enr", "enrolled"],
    "capacity": ["cap", "capacity"],
    "enr_cap": ["enr cap"],
    "faculty": ["faculty", "instructor"],
    "room": ["room", "classroom"],
}

HEADER_HINTS = {
    "School",
    "Level",
    "Course Abbr",
    "S/T",
    "Course Title",
    "Cr(ECTS)",
    "Cr(US)",
    "Start Date",
    "End Date",
    "Days",
    "Time",
    "Enr",
    "Cap",
    "Faculty",
    "Room",
}

DATE_FORMATS = (
    "%d-%b-%y",
    "%d-%b-%Y",
    "%Y-%m-%d",
)
CODE_PATTERN = re.compile(r"([A-Z]{2,})[\s,;:/-]*([0-9]{2,4}[A-Z]?)")


def parse_pdf_courses(
    file_path: str,
) -> tuple[list[CourseEntity], list[dict[str, object]]]:
    df = _read_table(file_path)
    df = _apply_real_header(df)
    df = df.where(pd.notnull(df), None)
    code_col, title_col, ects_col = _required_columns(df)
    optional_cols = _resolve_optional_columns(df)
    courses, errors = _build_courses(
        df,
        code_col,
        title_col,
        ects_col,
        optional_cols,
    )
    logger.info(
        "Course PDF parsed.",
        extra={
            "file_path": file_path,
            "table_rows": len(df),
            "parsed_courses": len(courses),
            "invalid_rows_count": len(errors),
        },
    )
    return courses, errors


def _simplify(value: str | None) -> str:
    if value is None:
        return ""
    text = str(value).lower().strip()
    text = re.sub(r"[()]", " ", text)
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def _norm_cols(columns: list[str]) -> list[str]:
    return [_simplify(col) for col in columns]


def _extract_pdf_rows(file_path: str) -> list[list[str | None]]:
    rows: list[list[str | None]] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables() or []:
                rows.extend(table)
    cleaned = [row for row in rows if row and any(cell for cell in row)]
    if not cleaned:
        raise ValueError("No table content found in PDF.")
    width = max(len(row) for row in cleaned)
    return [row + [None] * (width - len(row)) for row in cleaned]


def _read_table(file_path: str) -> pd.DataFrame:
    rows = _extract_pdf_rows(file_path)
    return pd.DataFrame(rows)


def _row_score(row: list[str]) -> int:
    hints = sum(1 for cell in row if cell in HEADER_HINTS)
    non_empty = sum(1 for cell in row if cell not in ("", "None", "nan"))
    return hints * 10 + non_empty


def _apply_real_header(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    best_index = 0
    best_score = -1
    for index in range(min(30, len(df))):
        row = [str(value).strip() for value in df.iloc[index].tolist()]
        score = _row_score(row)
        if score > best_score:
            best_score = score
            best_index = index
    header = [str(value).strip() for value in df.iloc[best_index].tolist()]
    body = df.iloc[best_index + 1 :].reset_index(drop=True)
    body.columns = header
    return body


def _find_col(df: pd.DataFrame, key: str) -> str | None:
    aliases = [_simplify(value) for value in COLUMN_MAP[key]]
    for idx, column in enumerate(_norm_cols(list(df.columns))):
        if column in aliases:
            return str(df.columns[idx])
    return None


def _required_columns(df: pd.DataFrame) -> tuple[str, str, str]:
    code_col = _find_col(df, "code")
    title_col = _find_col(df, "title")
    ects_col = _find_col(df, "ects")
    missing: list[str] = []
    if not code_col:
        missing.append("code")
    if not title_col:
        missing.append("title")
    if not ects_col:
        missing.append("ects")
    if missing:
        raise ValueError(
            f"Missing required columns: {missing}. Found: {list(df.columns)}"
        )
    return code_col, title_col, ects_col


def _resolve_optional_columns(df: pd.DataFrame) -> dict[str, str | None]:
    keys = [
        "level",
        "description",
        "school",
        "section",
        "credits_us",
        "start_date",
        "end_date",
        "days",
        "meeting_time",
        "enrolled",
        "capacity",
        "enr_cap",
        "faculty",
        "room",
    ]
    return {key: _find_col(df, key) for key in keys}


def _to_optional_non_negative_int(value: object) -> int | None:
    text = _as_text(value).replace(",", ".")
    if not text:
        return None
    try:
        number = int(float(text))
        return number if number >= 0 else None
    except Exception:
        match = re.search(r"-?\d+(?:\.\d+)?", text)
        if not match:
            return None
        number = int(float(match.group(0)))
        return number if number >= 0 else None


def _to_optional_int(value: object) -> int | None:
    text = _as_text(value)
    if not text:
        return None
    try:
        return int(float(text))
    except Exception:
        return None


def _to_optional_float(value: object) -> float | None:
    text = _as_text(value)
    if not text:
        return None
    try:
        return float(text)
    except Exception:
        return None


def _to_optional_date(value: object) -> date | None:
    text = _as_text(value)
    if not text:
        return None
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _as_text(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_text(raw: str) -> str:
    text = re.sub(r"\s+", " ", raw).strip().upper()
    return text


def _extract_level_token(raw: str) -> str:
    compact = re.sub(r"[^A-Z0-9]", "", _normalize_text(raw))
    match = re.search(r"[0-9]{1,4}[A-Z]?", compact)
    return match.group(0) if match else ""


def _parse_code_and_level(raw: str) -> tuple[str, str]:
    text = _normalize_text(raw)
    match = CODE_PATTERN.search(text)
    if match:
        return match.group(1), match.group(2)
    fallback = re.match(r"([A-Z]{2,})", text)
    if fallback:
        return fallback.group(1), ""
    return text, ""


def _resolve_level(
    level: str,
    row: pd.Series,
    level_col: str | None,
) -> str:
    row_level = (
        _extract_level_token(_as_text(row.get(level_col)))
        if level_col
        else ""
    )
    if row_level:
        return row_level
    return level


def _validate_row(
    raw: str,
    title: str,
    ects: int | None,
    level: str,
) -> None:
    if not raw:
        raise ValueError("Missing course code.")
    if not title:
        raise ValueError("Missing course title.")
    if ects is None:
        raise ValueError("Invalid ECTS value.")
    if not level:
        raise ValueError("Invalid course level.")


def _extract_enrollment_fields(
    row: pd.Series,
    cols: dict[str, str | None],
) -> tuple[int | None, int | None]:
    enrolled = None
    capacity = None

    enrolled_col = cols.get("enrolled")
    capacity_col = cols.get("capacity")
    enr_cap_col = cols.get("enr_cap")

    if enrolled_col:
        enrolled = _to_optional_int(row.get(enrolled_col))
    if capacity_col:
        capacity = _to_optional_int(row.get(capacity_col))

    if enrolled is not None and capacity is not None:
        return enrolled, capacity

    if enr_cap_col:
        text = _as_text(row.get(enr_cap_col))
        values = [int(match) for match in re.findall(r"\d+", text)]
        if enrolled is None and values:
            enrolled = values[0]
        if capacity is None and len(values) >= 2:
            capacity = values[1]

    return enrolled, capacity


def _text_from_column(
    row: pd.Series,
    cols: dict[str, str | None],
    key: str,
) -> str | None:
    column = cols.get(key)
    if not column:
        return None
    text = _as_text(row.get(column))
    return text or None


def _build_entity(
    code: str,
    title: str,
    subjects: list[str],
    level: str,
    ects: int,
    row: pd.Series,
    cols: dict[str, str | None],
) -> CourseEntity:
    level_col = cols.get("level")
    raw_level = _as_text(row.get(level_col)) if level_col else ""
    credits_us_col = cols.get("credits_us")
    start_date_col = cols.get("start_date")
    end_date_col = cols.get("end_date")

    enrolled, capacity = _extract_enrollment_fields(row, cols)
    department = ", ".join(subjects) if subjects else None

    return CourseEntity(
        code=code,
        title=title,
        department=department,
        level=level,
        ects=ects,
        description=_text_from_column(row, cols, "description"),
        school=_text_from_column(row, cols, "school"),
        academic_level=raw_level or None,
        section=_text_from_column(row, cols, "section"),
        credits_us=_to_optional_float(
            row.get(credits_us_col) if credits_us_col else None
        ),
        start_date=_to_optional_date(
            row.get(start_date_col) if start_date_col else None
        ),
        end_date=_to_optional_date(
            row.get(end_date_col) if end_date_col else None
        ),
        days=_text_from_column(row, cols, "days"),
        meeting_time=_text_from_column(row, cols, "meeting_time"),
        enrolled=enrolled,
        capacity=capacity,
        faculty=_text_from_column(row, cols, "faculty"),
        room=_text_from_column(row, cols, "room"),
    )


def _read_row(
    row: pd.Series,
    code_col: str,
    title_col: str,
    ects_col: str,
) -> tuple[str, str, int | None]:
    raw = _as_text(row.get(code_col))
    title = _as_text(row.get(title_col))
    ects = _to_optional_non_negative_int(row.get(ects_col))
    return raw, title, ects


def _parse_row(
    row: pd.Series,
    code_col: str,
    title_col: str,
    ects_col: str,
    cols: dict[str, str | None],
) -> CourseEntity | None:
    raw, title, ects = _read_row(row, code_col, title_col, ects_col)
    if not raw and not title and ects is None:
        return None

    code, level = _parse_code_and_level(raw)
    level = _resolve_level(level, row, cols.get("level"))
    _validate_row(raw, title, ects, level)
    subjects = [code] if code else []
    try:
        return _build_entity(
            code,
            title,
            subjects,
            level,
            ects,
            row,
            cols,
        )
    except ValidationError as exc:
        first_error = exc.errors()[0]
        error_msg = first_error.get("msg", "Invalid course row.")
        raise ValueError(str(error_msg)) from exc


def _build_courses(
    df: pd.DataFrame,
    code_col: str,
    title_col: str,
    ects_col: str,
    cols: dict[str, str | None],
) -> tuple[list[CourseEntity], list[dict[str, object]]]:
    courses: list[CourseEntity] = []
    errors: list[dict[str, object]] = []

    for idx, row in df.iterrows():
        try:
            course = _parse_row(
                row,
                code_col,
                title_col,
                ects_col,
                cols,
            )
        except ValueError as exc:
            code = _as_text(row.get(code_col)) or None
            title = _as_text(row.get(title_col)) or None
            error_info = {
                "row": idx + 1,
                "course_code": code,
                "course_name": title,
                "error": str(exc),
            }
            errors.append(error_info)
            logger.warning(
                "Invalid course schedule row.",
                extra={
                    **error_info,
                    "raw_ects": _as_text(row.get(ects_col)) or None,
                },
            )
            continue

        if course:
            courses.append(course)

    return courses, errors
