import re

SEMESTER_TERM_ORDER = {
    "spring": 0,
    "summer": 1,
    "fall": 2,
}
SEMESTER_LAST = (9999, 99, "zzzz")


def semester_sort_key(semester: str) -> tuple[int, int, str]:
    text = (semester or "").strip()
    if not text:
        return SEMESTER_LAST

    pattern = r"(?P<term>spring|summer|fall)\s*(?P<year>\d{4})?"
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return SEMESTER_LAST

    term = SEMESTER_TERM_ORDER.get(match.group("term").lower(), 99)
    year_text = match.group("year")
    year = int(year_text) if year_text else 9999
    return (year, term, text.lower())


def semester_desc_sort_key(semester: str) -> tuple[int, int, int, str]:
    year, term, text = semester_sort_key(semester)
    unknown = int((year, term, text) == SEMESTER_LAST)
    return (unknown, -year, -term, text)
