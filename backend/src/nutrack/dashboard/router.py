from fastapi import APIRouter, Depends

from nutrack.auth.dependencies import get_current_user
from nutrack.config import settings
from nutrack.dashboard.dependencies import get_dashboard_service
from nutrack.dashboard.schemas import AISummaryResponse, DashboardResponse
from nutrack.dashboard.service import DashboardService
from nutrack.shared.api.response import ApiResponse
from nutrack.users.models import User

router = APIRouter(tags=["dashboard"])


@router.get("", response_model=ApiResponse[DashboardResponse])
async def get_dashboard(
    user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> ApiResponse[DashboardResponse]:
    data = await service.get_dashboard(user.id, settings.CURRENT_TERM, settings.CURRENT_YEAR)
    return ApiResponse(data=data)


@router.post("/ai-summary", response_model=ApiResponse[AISummaryResponse])
async def get_ai_summary(
    user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
) -> ApiResponse[AISummaryResponse]:
    data = await service.get_ai_summary(user.id, settings.CURRENT_TERM, settings.CURRENT_YEAR)
    return ApiResponse(data=data)
