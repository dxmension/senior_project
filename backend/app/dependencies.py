from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.exceptions import InvalidTokenError, ForbiddenError
from app.models.user import User
from app.redis import get_redis
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.transcript import TranscriptService
from app.services.user import UserService
from app.utils.jwt import JWTService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/google/callback")


async def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
    redis: Redis = Depends(get_redis),
) -> AuthService:
    return AuthService(session=session, redis=redis)


async def get_transcript_service(
    session: AsyncSession = Depends(get_async_session),
) -> TranscriptService:
    return TranscriptService(session=session)


async def get_user_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserService:
    return UserService(session=session)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
) -> User:
    jwt_service = JWTService()
    payload = jwt_service.decode_access_token(token)
    if not payload:
        raise InvalidTokenError()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError()

    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise InvalidTokenError()

    user = await UserRepository(session).get_by_id(user_id_int)
    if not user:
        raise InvalidTokenError("User not found")

    return user


async def get_current_onboarded_user(user: User = Depends(get_current_user),) -> User:
    if not user.is_onboarded:
        raise ForbiddenError("Onboarding not completed")
    return user
