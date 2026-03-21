from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.admin.repository import AdminRepository
from nutrack.admin.service import AdminService
from nutrack.database import get_async_session
from nutrack.redis import get_redis


def get_admin_repository(
    session: AsyncSession = Depends(get_async_session),
) -> AdminRepository:
    return AdminRepository(session)


def get_admin_service(
    repository: AdminRepository = Depends(get_admin_repository),
    redis: Redis = Depends(get_redis),
) -> AdminService:
    return AdminService(repository, redis)
