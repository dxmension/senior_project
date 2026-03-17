from datetime import UTC, date, datetime

VALID_TERMS = ("Spring", "Summer", "Fall")
TERM_ORDER = {
    "Spring": 0,
    "Summer": 1,
    "Fall": 2,
}


def normalize_term(term: str) -> str:
    normalized = (term or "").strip().capitalize()
    if normalized not in VALID_TERMS:
        raise ValueError(f"Invalid term: {term}")
    return normalized


def term_order(term: str) -> int:
    normalized = (term or "").strip().capitalize()
    return TERM_ORDER.get(normalized, 99)


def format_term_year(term: str, year: int) -> str:
    return f"{normalize_term(term)} {year}"


def current_term_year(today: date | None = None) -> tuple[str, int]:
    current = today or datetime.now(UTC).date()
    if current.month <= 5:
        return ("Spring", current.year)
    if current.month <= 8:
        return ("Summer", current.year)
    return ("Fall", current.year)


def term_year_sort_key(term: str, year: int) -> tuple[int, int, str]:
    normalized = (term or "").strip().capitalize()
    order = term_order(normalized)
    unknown = int(not year or order == 99)
    return (unknown, year or 9999, order)


def term_year_desc_sort_key(term: str, year: int) -> tuple[int, int, int]:
    unknown, safe_year, order = term_year_sort_key(term, year)
    return (unknown, -safe_year, -order)
