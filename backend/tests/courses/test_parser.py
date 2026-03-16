import pandas as pd

from nutrack.courses import parser


def test_build_courses_keeps_rows_with_same_subject_and_level() -> None:
    df = pd.DataFrame(
        [
            {
                "Course Abbr": "NUSM 411A",
                "Course Title": "Basics of Physical Examination",
                "Cr(ECTS)": "2",
            },
            {
                "Course Abbr": "NUSM 411B",
                "Course Title": "Behavioral Medicine",
                "Cr(ECTS)": "3",
            },
        ]
    )

    courses, errors = parser._build_courses(  # noqa: SLF001
        df,
        "Course Abbr",
        "Course Title",
        "Cr(ECTS)",
        {},
    )

    assert not errors
    assert len(courses) == 2
    assert [course.code for course in courses] == ["NUSM", "NUSM"]
    assert [course.level for course in courses] == ["411A", "411B"]


def test_build_courses_accepts_zero_ects() -> None:
    df = pd.DataFrame(
        [
            {
                "Course Abbr": "NUSM 417",
                "Course Title": "Clinical Experiences",
                "Cr(ECTS)": "0",
            }
        ]
    )

    courses, errors = parser._build_courses(  # noqa: SLF001
        df,
        "Course Abbr",
        "Course Title",
        "Cr(ECTS)",
        {},
    )

    assert not errors
    assert len(courses) == 1
    assert courses[0].ects == 0
    assert courses[0].code == "NUSM"
    assert courses[0].level == "417"


def test_build_courses_parses_comma_separated_code_level() -> None:
    df = pd.DataFrame(
        [
            {
                "Course Abbr": "NUSM,407",
                "Course Title": "Clinical Module",
                "Cr(ECTS)": "4",
            }
        ]
    )

    courses, errors = parser._build_courses(  # noqa: SLF001
        df,
        "Course Abbr",
        "Course Title",
        "Cr(ECTS)",
        {},
    )

    assert not errors
    assert len(courses) == 1
    assert courses[0].code == "NUSM"
    assert courses[0].level == "407"


def test_build_courses_prefers_level_column_with_letter_suffix() -> None:
    df = pd.DataFrame(
        [
            {
                "Course Abbr": "NUSM",
                "Level": "411 B",
                "Course Title": "Basics of Physical Examination",
                "Cr(ECTS)": "2",
            }
        ]
    )

    courses, errors = parser._build_courses(  # noqa: SLF001
        df,
        "Course Abbr",
        "Course Title",
        "Cr(ECTS)",
        {"level": "Level"},
    )

    assert not errors
    assert len(courses) == 1
    assert courses[0].code == "NUSM"
    assert courses[0].level == "411B"
