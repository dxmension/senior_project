from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.config import settings
from nutrack.courses.service import CourseSearchService


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

