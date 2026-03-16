from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.auth.exceptions import InvalidTokenError
from nutrack.auth.security import JWTService
from nutrack.database import get_async_session
from nutrack.users.exceptions import ForbiddenError
from nutrack.users.models import User
from nutrack.users.repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


def _get_user_id(payload: dict) -> int:
    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError()
    try:
        return int(user_id)
    except (TypeError, ValueError):
        raise InvalidTokenError()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(
        bearer_scheme
    ),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    if not credentials:
        raise InvalidTokenError()
    if credentials.scheme.lower() != "bearer":
        raise InvalidTokenError()
    token = credentials.credentials
    payload = JWTService().decode_access_token(token)
    if not payload:
        raise InvalidTokenError()

    user = await UserRepository(session).get_by_id(_get_user_id(payload))
    if not user:
        raise InvalidTokenError("User not found")
    return user


async def get_current_onboarded_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_onboarded:
        raise ForbiddenError("Onboarding not completed")
    return user


async def get_current_admin_user(
    user: User = Depends(get_current_user),
) -> User:
    if not user.is_admin:
        raise ForbiddenError("Admin access required")
    return user
