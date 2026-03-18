from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.dialects import postgresql

from nutrack.courses.models import Course, CourseOffering
from nutrack.courses.repository import CourseOfferingRepository


def _result_with(*courses: Course) -> SimpleNamespace:
    scalars = SimpleNamespace(all=lambda: list(courses))
    return SimpleNamespace(scalars=lambda: scalars)


def _compiled_sql(statement) -> str:
    return str(statement.compile(dialect=postgresql.dialect()))


@pytest.mark.asyncio
async def test_search_prioritizes_code_matches_in_ordering() -> None:
    course = Course(
        id=7,
        code="CSCI",
        level="151",
        title="Programming",
        ects=6,
    )
    offering = CourseOffering(
        id=9,
        course_id=7,
        course=course,
        term="Spring",
        year=2026,
    )
    session = SimpleNamespace(
        execute=AsyncMock(return_value=_result_with(offering))
    )
    repository = CourseOfferingRepository(session)

    courses = await repository.search("cs", 10, "Spring", 2026)

    statement = session.execute.await_args.args[0]
    sql = _compiled_sql(statement)

    assert courses == [offering]
    assert "courses.code ILIKE" in sql
    assert "courses.title ILIKE" in sql
    assert "courses.level ILIKE" in sql
    assert "concat(courses.code, " in sql
    assert "ORDER BY CASE WHEN (concat(courses.code, " in sql
    assert "course_offerings.term = " in sql
