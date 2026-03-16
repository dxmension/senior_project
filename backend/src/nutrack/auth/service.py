from urllib.parse import urlencode

from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.auth.exceptions import (
    InvalidEmailDomainError,
    InvalidTokenError,
    OAuthError,
)
from nutrack.auth.repository import AuthUserRepository
from nutrack.auth.security import JWTService
from nutrack.config import settings

REFRESH_TOKEN_PREFIX = "refresh_token:"


class AuthService:
    GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
    GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.user_repo = AuthUserRepository(session)
        self.redis = redis
        self.jwt = JWTService()

    def get_google_auth_url(self) -> str:
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid profile email",
            "access_type": "offline",
            "prompt": "consent",
        }
        return f"{self.GOOGLE_AUTH_URL}?{urlencode(params)}"

    async def _exchange_token(self, code: str) -> dict:
        async with AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url=self.GOOGLE_TOKEN_URL,
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                },
            )

        if response.status_code != 200:
            raise OAuthError(f"Google token exchange failed: {response.text}")

        return response.json()

    async def _get_user_info(self, access_token: str) -> dict:
        async with AsyncClient(timeout=15.0) as client:
            response = await client.get(
                self.GOOGLE_USERINFO_URL,
                headers={"Authorization": f"Bearer {access_token}"},
            )

        if response.status_code != 200:
            raise OAuthError("Failed to fetch user info from Google")

        return response.json()

    async def _store_refresh_token(self, user_id: str, jti: str) -> None:
        key = f"{REFRESH_TOKEN_PREFIX}{jti}"
        ttl = settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400
        await self.redis.set(key, user_id, ex=ttl)

    async def _revoke_refresh_token(self, jti: str) -> None:
        key = f"{REFRESH_TOKEN_PREFIX}{jti}"
        await self.redis.delete(key)

    async def _issue_tokens(self, user_id: int) -> dict:
        access_token = self.jwt.create_access_token(user_id)
        refresh_token, jti = self.jwt.create_refresh_token(user_id)
        await self._store_refresh_token(str(user_id), jti)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def google_callback(self, code: str) -> dict:
        google_tokens = await self._exchange_token(code)
        user_info = await self._get_user_info(google_tokens["access_token"])

        if not user_info or not user_info.get("id"):
            raise OAuthError("Google returned invalid user info")

        email = user_info.get("email", "")
        if not email.endswith("@nu.edu.kz"):
            raise InvalidEmailDomainError()

        google_id = user_info["id"]
        user = await self.user_repo.get_by_google_id(google_id)
        if not user:
            user = await self.user_repo.create(
                email=email,
                google_id=google_id,
                first_name=user_info.get("given_name", ""),
                last_name=user_info.get("family_name", ""),
                avatar_url=user_info.get("picture"),
            )

        tokens = await self._issue_tokens(user.id)
        return {**tokens, "is_onboarded": user.is_onboarded}

    async def refresh(self, refresh_token: str) -> dict:
        payload = self.jwt.decode_refresh_token(refresh_token)
        if not payload:
            raise InvalidTokenError("Invalid refresh token")

        jti = payload["jti"]
        user_id = payload["sub"]

        key = f"{REFRESH_TOKEN_PREFIX}{jti}"
        stored = await self.redis.get(key)
        if not stored:
            raise InvalidTokenError("Refresh token revoked or expired")

        await self._revoke_refresh_token(jti)

        user = await self.user_repo.get_by_id(int(user_id))
        if not user:
            raise InvalidTokenError("User not found")

        return await self._issue_tokens(user.id)

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        payload = self.jwt.decode_refresh_token(refresh_token)
        if payload:
            await self._revoke_refresh_token(payload["jti"])
