from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.admin.repository import AdminRepository


@pytest.mark.asyncio
async def test_update_user_refreshes_user_after_flush() -> None:
    session = SimpleNamespace(
        flush=AsyncMock(),
        refresh=AsyncMock(),
    )
    repository = AdminRepository(session)
    user = SimpleNamespace(is_admin=False, study_year=2)

    updated = await repository.update_user(user, is_admin=True, study_year=3)

    assert updated is user
    assert user.is_admin is True
    assert user.study_year == 3
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_search_courses_matches_combined_code_and_level() -> None:
    result = SimpleNamespace(scalars=lambda: SimpleNamespace(all=lambda: []))
    session = SimpleNamespace(execute=AsyncMock(return_value=result))
    repository = AdminRepository(session)

    await repository.search_courses("biol 101")

    stmt = session.execute.await_args.args[0]
    compiled = str(stmt)
    lowered = compiled.lower()

    assert "courses.code" in lowered
    assert "courses.level" in lowered
    assert "courses.title" in lowered
