from fastapi import APIRouter, Depends

from app.dependencies import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import (
    GoogleAuthURL,
    GoogleCallback,
    TokenPair,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.common import ApiResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/google/url", response_model=ApiResponse[GoogleAuthURL])
async def google_auth_url(service: AuthService = Depends(get_auth_service),):
    url = service.get_google_auth_url()
    return ApiResponse(data=GoogleAuthURL(url=url))


@router.post("/google/callback", response_model=ApiResponse[TokenPair])
async def google_callback(
    body: GoogleCallback, service: AuthService = Depends(get_auth_service),
):
    result = await service.google_callback(body.code)
    return ApiResponse(data=TokenPair(**result))


@router.post("/refresh", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    body: RefreshRequest, service: AuthService = Depends(get_auth_service),
):
    result = await service.refresh(body.refresh_token)
    return ApiResponse(data=TokenResponse(**result))


@router.post("/logout", response_model=ApiResponse)
async def logout(
    body: RefreshRequest,
    service: AuthService = Depends(get_auth_service),
    user: User = Depends(get_current_user),
):
    await service.logout(body.refresh_token)
    return ApiResponse(message="Logged out successfully")
