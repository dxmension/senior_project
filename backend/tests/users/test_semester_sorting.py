from nutrack.users.utils import semester_desc_sort_key, semester_sort_key


def test_semester_sort_key_orders_year_then_term() -> None:
    semesters = [
        "Fall 2024",
        "Spring 2024",
        "Fall 2025",
        "Spring 2025",
    ]

    ordered = sorted(semesters, key=semester_sort_key)

    assert ordered == [
        "Spring 2024",
        "Fall 2024",
        "Spring 2025",
        "Fall 2025",
    ]


def test_semester_sort_key_keeps_unknown_values_last() -> None:
    semesters = [
        "Spring 2024",
        "",
        "Winter 2024",
        "Fall 2024",
    ]

    ordered = sorted(semesters, key=semester_sort_key)

    assert ordered == [
        "Spring 2024",
        "Fall 2024",
        "",
        "Winter 2024",
    ]


def test_semester_desc_sort_key_orders_latest_first() -> None:
    semesters = [
        "Fall 2024",
        "Spring 2024",
        "Fall 2025",
        "Spring 2025",
        "",
    ]

    ordered = sorted(semesters, key=semester_desc_sort_key)

    assert ordered == [
        "Fall 2025",
        "Spring 2025",
        "Fall 2024",
        "Spring 2024",
        "",
    ]
