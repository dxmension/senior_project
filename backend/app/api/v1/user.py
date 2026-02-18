from fastapi import APIRouter, Depends

from app.dependencies import get_current_user, get_user_service
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    EnrollmentResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
)
from app.services.user import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ApiResponse[UserProfileResponse])
async def get_me(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    profile = await service.get_profile(user.id)
    return ApiResponse(data=profile)


@router.patch("/me", response_model=ApiResponse[UserProfileResponse])
async def update_me(
    body: UserProfileUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    profile = await service.update_profile(user.id, body)
    return ApiResponse(data=profile)


@router.get("/enrollments", response_model=ApiResponse[list[EnrollmentResponse]])
async def get_enrollments(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    enrollments = await service.get_enrollments(user.id)
    return ApiResponse(data=enrollments)


@router.get("/stats", response_model=ApiResponse[UserStatsResponse])
async def get_stats(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    stats = await service.get_stats(user.id)
    return ApiResponse(data=stats)
