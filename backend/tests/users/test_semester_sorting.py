from nutrack.users.utils import term_year_desc_sort_key, term_year_sort_key


def test_term_year_sort_key_orders_year_then_term() -> None:
    semesters = [
        ("Fall", 2024),
        ("Spring", 2024),
        ("Fall", 2025),
        ("Spring", 2025),
    ]

    ordered = sorted(semesters, key=lambda item: term_year_sort_key(*item))

    assert ordered == [
        ("Spring", 2024),
        ("Fall", 2024),
        ("Spring", 2025),
        ("Fall", 2025),
    ]


def test_term_year_sort_key_keeps_unknown_values_last() -> None:
    semesters = [
        ("Spring", 2024),
        ("", 0),
        ("Winter", 2024),
        ("Fall", 2024),
    ]

    ordered = sorted(semesters, key=lambda item: term_year_sort_key(*item))

    assert ordered == [
        ("Spring", 2024),
        ("Fall", 2024),
        ("Winter", 2024),
        ("", 0),
    ]


def test_term_year_desc_sort_key_orders_latest_first() -> None:
    semesters = [
        ("Fall", 2024),
        ("Spring", 2024),
        ("Fall", 2025),
        ("Spring", 2025),
        ("", 0),
    ]

    ordered = sorted(
        semesters,
        key=lambda item: term_year_desc_sort_key(*item),
    )

    assert ordered == [
        ("Fall", 2025),
        ("Spring", 2025),
        ("Fall", 2024),
        ("Spring", 2024),
        ("", 0),
    ]
