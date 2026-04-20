from fastapi import APIRouter, Depends

from nutrack.auth.dependencies import get_current_onboarded_user
from nutrack.insights.dependencies import get_insights_service
from nutrack.insights.schemas import InsightsResponse
from nutrack.insights.service import InsightsService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(tags=["insights"])


@router.get("", response_model=ApiResponse[InsightsResponse])
async def get_insights(
    user: User = Depends(get_current_onboarded_user),
    service: InsightsService = Depends(get_insights_service),
) -> ApiResponse[InsightsResponse]:
    data = await service.get_or_generate(user.id, user)
    return ApiResponse(data=data)
