from fastapi import APIRouter, Depends

from nutrack.auth.dependencies import get_current_user
from nutrack.utils import ApiResponse
from nutrack.users.dependencies import get_user_service
from nutrack.users.models import User
from nutrack.users.schemas import (
    AuditResultResponse,
    EnrollmentResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
)
from nutrack.users.service import UserService

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("", response_model=ApiResponse[UserProfileResponse])
async def get_profile(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    profile = await service.get_profile(user.id)
    return ApiResponse(data=profile)


@router.patch("", response_model=ApiResponse[UserProfileResponse])
async def update_profile(
    body: UserProfileUpdate,
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    profile = await service.update_profile(user.id, body)
    return ApiResponse(data=profile)


@router.get(
    "/enrollments",
    response_model=ApiResponse[list[EnrollmentResponse]],
)
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


@router.get("/audit", response_model=ApiResponse[AuditResultResponse])
async def get_audit(
    user: User = Depends(get_current_user),
    service: UserService = Depends(get_user_service),
):
    audit = await service.get_audit(user.id)
    return ApiResponse(data=audit)
