from datetime import date

from nutrack.semester import current_term_year


def test_current_term_year_uses_spring_until_may() -> None:
    assert current_term_year(date(2026, 5, 15)) == ("Spring", 2026)


def test_current_term_year_uses_summer_from_june() -> None:
    assert current_term_year(date(2026, 6, 1)) == ("Summer", 2026)


def test_current_term_year_keeps_summer_in_august() -> None:
    assert current_term_year(date(2026, 8, 31)) == ("Summer", 2026)


def test_current_term_year_uses_fall_from_september() -> None:
    assert current_term_year(date(2026, 9, 1)) == ("Fall", 2026)
