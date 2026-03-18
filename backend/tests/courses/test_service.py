import logging

from nutrack.courses.domain import CourseEntity
from nutrack.courses import service


def test_log_duplicate_keys_handles_scoped_course_keys(
    caplog,
) -> None:
    courses = [
        CourseEntity(
            code="CSCI",
            level="151",
            title="Programming",
            ects=6,
            section="1",
        ),
        CourseEntity(
            code="CSCI",
            level="151",
            title="Programming",
            ects=6,
            section="1",
        ),
    ]

    with caplog.at_level(logging.WARNING, logger="nutrack.courses.service"):
        service._log_duplicate_keys(courses, "Fall", 2026)  # noqa: SLF001

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.duplicate_keys_count == 1
    assert record.sample_keys == [("CSCI", "151", "1", "Fall", 2026, 2)]
