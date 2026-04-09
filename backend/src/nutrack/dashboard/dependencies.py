from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.dashboard.service import DashboardService


def get_dashboard_service(
    db: AsyncSession = Depends(get_async_session),
) -> DashboardService:
    return DashboardService(db)
