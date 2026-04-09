from fastapi import APIRouter, Depends, status

from nutrack.auth.dependencies import get_current_user
from nutrack.categories.dependencies import get_category_service
from nutrack.categories.schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest,
)
from nutrack.categories.service import CategoryService
from nutrack.shared.api.response import ApiResponse
from nutrack.users.models import User

router = APIRouter(tags=["categories"])


@router.get("", response_model=ApiResponse[list[CategoryResponse]])
async def list_categories(
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    categories = await service.list_categories(user.id)
    return ApiResponse(data=categories)


@router.post(
    "",
    response_model=ApiResponse[CategoryResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    body: CreateCategoryRequest,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    category = await service.create_category(user.id, body)
    return ApiResponse(data=category)


@router.patch("/{category_id}", response_model=ApiResponse[CategoryResponse])
async def update_category(
    category_id: int,
    body: UpdateCategoryRequest,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    category = await service.update_category(user.id, category_id, body)
    return ApiResponse(data=category)


@router.delete("/{category_id}", response_model=ApiResponse[None])
async def delete_category(
    category_id: int,
    user: User = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
):
    await service.delete_category(user.id, category_id)
    return ApiResponse(data=None)
