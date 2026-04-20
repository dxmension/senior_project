from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.config import settings
from nutrack.courses.service import CourseSearchService
from nutrack.courses.schemas import (
    CourseSearchComponentGroup,
    CourseSearchGroup,
    CourseSearchOfferingOption,
)


def _make_offering(
    offering_id: int,
    section: str,
    faculty: str,
    days: str,
    meeting_time: str,
    room: str,
    enrolled: int,
    capacity: int,
) -> SimpleNamespace:
    course = SimpleNamespace(
        id=101,
        code="CS101",
        level="UG",
        title="Intro to Computer Science",
        ects=5,
    )
    return SimpleNamespace(
        id=offering_id,
        course=course,
        section=section,
        faculty=faculty,
        days=days,
        meeting_time=meeting_time,
        room=room,
        enrolled=enrolled,
        capacity=capacity,
        term="Fall",
        year=2026,
    )


@pytest.mark.asyncio
async def test_search_courses_uses_current_term_and_bounded_limit() -> None:
    repository = SimpleNamespace(search=AsyncMock(return_value=[]))
    service = CourseSearchService(repository=repository)

    result = await service.search_courses("cs", 30)

    assert result == []
    repository.search.assert_awaited_once_with(
        "cs",
        20,
        settings.CURRENT_TERM,
        settings.CURRENT_YEAR,
    )


@pytest.mark.asyncio
async def test_search_courses_groups_offerings_by_catalog_course() -> None:
    repository = SimpleNamespace(
        search=AsyncMock(
            return_value=[
                _make_offering(
                    11,
                    "L1",
                    "Dr. Ada",
                    "Mon/Wed",
                    "09:00-10:30",
                    "A101",
                    48,
                    60,
                ),
                _make_offering(
                    12,
                    "L2",
                    "Dr. Turing",
                    "Tue/Thu",
                    "11:00-12:30",
                    "A102",
                    45,
                    60,
                ),
            ]
        )
    )
    service = CourseSearchService(repository=repository)

    result = await service.search_courses("cs", 20)

    assert result == [
        CourseSearchGroup(
            course_id=101,
            code="CS101",
            level="UG",
            title="Intro to Computer Science",
            ects=5,
            term=settings.CURRENT_TERM,
            year=settings.CURRENT_YEAR,
            components=[
                CourseSearchComponentGroup(
                    component_type="lecture",
                    label="Lecture",
                    required=True,
                    offerings=[
                        CourseSearchOfferingOption(
                            offering_id=11,
                            section="L1",
                            faculty="Dr. Ada",
                            days="Mon/Wed",
                            meeting_time="09:00-10:30",
                            room="A101",
                            enrolled=48,
                            capacity=60,
                        ),
                        CourseSearchOfferingOption(
                            offering_id=12,
                            section="L2",
                            faculty="Dr. Turing",
                            days="Tue/Thu",
                            meeting_time="11:00-12:30",
                            room="A102",
                            enrolled=45,
                            capacity=60,
                        ),
                    ],
                )
            ],
        )
    ]


@pytest.mark.parametrize(
    ("term", "year", "expected"),
    [
        ("fall", 2027, ("Fall", 2027)),
        (None, None, (settings.CURRENT_TERM, settings.CURRENT_YEAR)),
    ],
)
def test_resolve_term_year_accepts_valid_inputs(
    term: str | None,
    year: int | None,
    expected: tuple[str, int],
) -> None:
    service = CourseSearchService(repository=object())

    assert service._resolve_term_year(term, year) == expected  # noqa: SLF001


def test_resolve_term_year_requires_term_and_year_together() -> None:
    from nutrack.courses.exceptions import CourseSearchError

    service = CourseSearchService(repository=object())

    with pytest.raises(CourseSearchError, match="provided together"):
        service._resolve_term_year("Fall", None)  # noqa: SLF001

