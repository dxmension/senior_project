from fastapi import APIRouter, Depends

from nutrack.auth.schemas import (
    GoogleAuthURL,
    GoogleCallback,
    RefreshRequest,
    TokenPair,
    TokenResponse,
)
from nutrack.auth.service import AuthService
from nutrack.auth.dependencies import get_current_user
from nutrack.auth.dependencies_services import get_auth_service
from nutrack.utils import ApiResponse
from nutrack.users.models import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google-url", response_model=ApiResponse[GoogleAuthURL])
async def google_auth_url(service: AuthService = Depends(get_auth_service)):
    url = service.get_google_auth_url()
    return ApiResponse(data=GoogleAuthURL(url=url))


@router.post("/google-callback", response_model=ApiResponse[TokenPair])
async def google_callback(
    body: GoogleCallback,
    service: AuthService = Depends(get_auth_service),
):
    result = await service.google_callback(body.code)
    return ApiResponse(data=TokenPair(**result))


@router.post("/tokens/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    body: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
):
    result = await service.refresh(body.refresh_token)
    return ApiResponse(data=TokenResponse(**result))


@router.post("/tokens/revoke", response_model=ApiResponse)
async def revoke_token(
    body: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
    user: User = Depends(get_current_user),
):
    await service.revoke_refresh_token(body.refresh_token)
    return ApiResponse(data={"revoked": True}, meta={"user_id": user.id})
