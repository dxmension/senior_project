from datetime import datetime, timedelta, timezone
from uuid import uuid4

from jose import JWTError, jwt

from nutrack.config import settings


class JWTService:
    def create_access_token(self, user_id: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": str(user_id),
            "type": "access",
            "iat": now,
            "exp": now
            + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
            "jti": str(uuid4()),
        }
        return jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )

    def create_refresh_token(self, user_id: int) -> tuple[str, str]:
        now = datetime.now(timezone.utc)
        jti = str(uuid4())
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            "jti": jti,
        }
        token = jwt.encode(
            payload,
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        return token, jti

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except JWTError:
            return {}

    def decode_access_token(self, token: str) -> dict:
        payload = self.decode_token(token)
        if payload.get("type") != "access":
            return {}
        return payload

    def decode_refresh_token(self, token: str) -> dict:
        payload = self.decode_token(token)
        if payload.get("type") != "refresh":
            return {}
        return payload
