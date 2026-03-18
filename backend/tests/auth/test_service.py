from types import SimpleNamespace
from unittest.mock import AsyncMock
from urllib.parse import parse_qs, urlparse

import pytest

from nutrack.auth.exceptions import InvalidEmailDomainError, InvalidTokenError
from nutrack.auth.service import AuthService


def _service() -> AuthService:
    redis = SimpleNamespace(set=AsyncMock(), get=AsyncMock(), delete=AsyncMock())
    return AuthService(session=None, redis=redis)


def test_get_google_auth_url_contains_expected_query_params() -> None:
    service = _service()

    parsed = urlparse(service.get_google_auth_url())
    params = parse_qs(parsed.query)

    assert parsed.scheme == "https"
    assert params["response_type"] == ["code"]
    assert params["scope"] == ["openid profile email"]
    assert params["access_type"] == ["offline"]


@pytest.mark.asyncio
async def test_google_callback_creates_user_and_issues_tokens() -> None:
    service = _service()
    created_user = SimpleNamespace(id=8, is_onboarded=False)
    service._exchange_token = AsyncMock(return_value={"access_token": "google"})
    service._get_user_info = AsyncMock(
        return_value={
            "id": "google-id",
            "email": "student@nu.edu.kz",
            "given_name": "John",
            "family_name": "Doe",
            "picture": "https://avatar.test",
        }
    )
    service._issue_tokens = AsyncMock(
        return_value={
            "access_token": "access",
            "refresh_token": "refresh",
            "token_type": "bearer",
        }
    )
    service.user_repo.get_by_google_id = AsyncMock(return_value=None)
    service.user_repo.create = AsyncMock(return_value=created_user)

    result = await service.google_callback("code")

    assert result["access_token"] == "access"
    assert result["is_onboarded"] is False
    service.user_repo.create.assert_awaited_once_with(
        email="student@nu.edu.kz",
        google_id="google-id",
        first_name="John",
        last_name="Doe",
        avatar_url="https://avatar.test",
    )
    service._issue_tokens.assert_awaited_once_with(8)


@pytest.mark.asyncio
async def test_google_callback_rejects_non_nu_email() -> None:
    service = _service()
    service._exchange_token = AsyncMock(return_value={"access_token": "google"})
    service._get_user_info = AsyncMock(
        return_value={"id": "google-id", "email": "student@example.com"}
    )

    with pytest.raises(InvalidEmailDomainError):
        await service.google_callback("code")


@pytest.mark.asyncio
async def test_refresh_reissues_tokens_for_valid_refresh_token() -> None:
    service = _service()
    service.jwt = SimpleNamespace(
        decode_refresh_token=lambda token: {"jti": "jti-1", "sub": "12"}
    )
    service.redis.get = AsyncMock(return_value="12")
    service._revoke_refresh_token = AsyncMock()
    service._issue_tokens = AsyncMock(
        return_value={
            "access_token": "new-access",
            "refresh_token": "new-refresh",
            "token_type": "bearer",
        }
    )
    service.user_repo.get_by_id = AsyncMock(return_value=SimpleNamespace(id=12))

    result = await service.refresh("refresh-token")

    assert result["access_token"] == "new-access"
    service.redis.get.assert_awaited_once_with("refresh_token:jti-1")
    service._revoke_refresh_token.assert_awaited_once_with("jti-1")
    service._issue_tokens.assert_awaited_once_with(12)


@pytest.mark.asyncio
async def test_refresh_rejects_revoked_token() -> None:
    service = _service()
    service.jwt = SimpleNamespace(
        decode_refresh_token=lambda token: {"jti": "jti-2", "sub": "12"}
    )
    service.redis.get = AsyncMock(return_value=None)

    with pytest.raises(InvalidTokenError):
        await service.refresh("refresh-token")


@pytest.mark.asyncio
async def test_revoke_refresh_token_ignores_invalid_payload() -> None:
    service = _service()
    service.jwt = SimpleNamespace(decode_refresh_token=lambda token: {})
    service._revoke_refresh_token = AsyncMock()

    await service.revoke_refresh_token("refresh-token")

    service._revoke_refresh_token.assert_not_called()
