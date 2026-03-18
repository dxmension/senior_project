from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_user
from nutrack.auth.dependencies_services import get_auth_service


@pytest.mark.asyncio
async def test_google_auth_url_returns_service_url(client, test_app) -> None:
    service = SimpleNamespace(get_google_auth_url=lambda: "https://example.com")
    test_app.dependency_overrides[get_auth_service] = lambda: service

    response = await client.get("/v1/auth/google-url")

    assert response.status_code == 200
    assert response.json()["data"] == {"url": "https://example.com"}


@pytest.mark.asyncio
async def test_google_callback_returns_token_pair(client, test_app) -> None:
    payload = {
        "access_token": "access",
        "refresh_token": "refresh",
        "token_type": "bearer",
        "is_onboarded": True,
    }
    service = SimpleNamespace(google_callback=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_auth_service] = lambda: service

    response = await client.post(
        "/v1/auth/google-callback",
        json={"code": "google-code"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == payload
    service.google_callback.assert_awaited_once_with("google-code")


@pytest.mark.asyncio
async def test_refresh_token_returns_new_pair(client, test_app) -> None:
    payload = {
        "access_token": "new-access",
        "refresh_token": "new-refresh",
        "token_type": "bearer",
    }
    service = SimpleNamespace(refresh=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_auth_service] = lambda: service

    response = await client.post(
        "/v1/auth/tokens/refresh",
        json={"refresh_token": "old-refresh"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == payload
    service.refresh.assert_awaited_once_with("old-refresh")


@pytest.mark.asyncio
async def test_revoke_token_requires_auth(client, test_app) -> None:
    service = SimpleNamespace(revoke_refresh_token=AsyncMock())
    test_app.dependency_overrides[get_auth_service] = lambda: service

    response = await client.post(
        "/v1/auth/tokens/revoke",
        json={"refresh_token": "refresh"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_revoke_token_returns_revoked_flag(client, test_app) -> None:
    service = SimpleNamespace(revoke_refresh_token=AsyncMock())
    test_app.dependency_overrides[get_auth_service] = lambda: service
    test_app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=3)

    response = await client.post(
        "/v1/auth/tokens/revoke",
        json={"refresh_token": "refresh"},
    )

    assert response.status_code == 200
    assert response.json()["data"] == {"revoked": True}
    assert response.json()["meta"] == {"user_id": 3}
    service.revoke_refresh_token.assert_awaited_once_with("refresh")

