from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import (
    _get_user_id,
    get_current_admin_user,
    get_current_onboarded_user,
    get_current_user,
)
from nutrack.auth.exceptions import InvalidTokenError
from nutrack.users.exceptions import ForbiddenError


def test_get_user_id_returns_int() -> None:
    assert _get_user_id({"sub": "7"}) == 7


@pytest.mark.parametrize("payload", [{}, {"sub": None}, {"sub": "abc"}])
def test_get_user_id_rejects_invalid_payload(payload: dict[str, object]) -> None:
    with pytest.raises(InvalidTokenError):
        _get_user_id(payload)


@pytest.mark.asyncio
async def test_get_current_user_requires_credentials() -> None:
    with pytest.raises(InvalidTokenError):
        await get_current_user(credentials=None, session=object())


@pytest.mark.asyncio
async def test_get_current_user_requires_bearer_scheme() -> None:
    credentials = SimpleNamespace(scheme="basic", credentials="token")

    with pytest.raises(InvalidTokenError):
        await get_current_user(credentials=credentials, session=object())


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token(monkeypatch) -> None:
    monkeypatch.setattr(
        "nutrack.auth.dependencies.JWTService.decode_access_token",
        lambda self, token: {},
    )
    credentials = SimpleNamespace(scheme="Bearer", credentials="token")

    with pytest.raises(InvalidTokenError):
        await get_current_user(credentials=credentials, session=object())


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_user(monkeypatch) -> None:
    monkeypatch.setattr(
        "nutrack.auth.dependencies.JWTService.decode_access_token",
        lambda self, token: {"sub": "9"},
    )
    user_lookup = AsyncMock(return_value=None)
    monkeypatch.setattr(
        "nutrack.auth.dependencies.UserRepository.get_by_id",
        user_lookup,
    )
    credentials = SimpleNamespace(scheme="Bearer", credentials="token")

    with pytest.raises(InvalidTokenError):
        await get_current_user(credentials=credentials, session=object())


@pytest.mark.asyncio
async def test_get_current_user_returns_loaded_user(monkeypatch) -> None:
    user = SimpleNamespace(id=9, email="student@nu.edu.kz")
    monkeypatch.setattr(
        "nutrack.auth.dependencies.JWTService.decode_access_token",
        lambda self, token: {"sub": "9"},
    )
    user_lookup = AsyncMock(return_value=user)
    monkeypatch.setattr(
        "nutrack.auth.dependencies.UserRepository.get_by_id",
        user_lookup,
    )
    credentials = SimpleNamespace(scheme="Bearer", credentials="token")

    result = await get_current_user(credentials=credentials, session=object())

    assert result is user
    user_lookup.assert_awaited_once_with(9)


@pytest.mark.asyncio
async def test_get_current_onboarded_user_rejects_pending_user() -> None:
    user = SimpleNamespace(is_onboarded=False)

    with pytest.raises(ForbiddenError):
        await get_current_onboarded_user(user)


@pytest.mark.asyncio
async def test_get_current_onboarded_user_returns_user() -> None:
    user = SimpleNamespace(is_onboarded=True)

    assert await get_current_onboarded_user(user) is user


@pytest.mark.asyncio
async def test_get_current_admin_user_rejects_non_admin() -> None:
    user = SimpleNamespace(is_admin=False)

    with pytest.raises(ForbiddenError):
        await get_current_admin_user(user)


@pytest.mark.asyncio
async def test_get_current_admin_user_returns_user() -> None:
    user = SimpleNamespace(is_admin=True)

    assert await get_current_admin_user(user) is user

