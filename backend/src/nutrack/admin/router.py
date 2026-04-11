from fastapi import APIRouter, Depends, Query

from nutrack.admin.dependencies import get_admin_service
from nutrack.admin.schemas import (
    AnalyticsOverview,
    CourseListItem,
    CourseUpdateRequest,
    DatabaseHealth,
    DatabaseStats,
    UserDetail,
    UserListItem,
    UserUpdateRequest,
)
from nutrack.admin.service import AdminService
from nutrack.auth.dependencies import get_current_admin_user
from nutrack.utils import ApiResponse
from nutrack.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=ApiResponse[list[UserListItem]])
async def get_all_users(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    users = await service.get_all_users(skip, limit)
    return ApiResponse(data=users)


@router.get("/users/search", response_model=ApiResponse[list[UserListItem]])
async def search_users(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    users = await service.search_users(q, limit)
    return ApiResponse(data=users)


@router.get("/users/{user_id}", response_model=ApiResponse[UserDetail])
async def get_user_detail(
    user_id: int,
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    user = await service.get_user_detail(user_id)
    return ApiResponse(data=user)


@router.patch("/users/{user_id}", response_model=ApiResponse[UserDetail])
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    user = await service.update_user(
        user_id=user_id,
        current_user_id=current_user.id,
        is_admin=update_data.is_admin,
        is_onboarded=update_data.is_onboarded,
        major=update_data.major,
        study_year=update_data.study_year,
    )
    return ApiResponse(data=user)


@router.get("/stats", response_model=ApiResponse[DatabaseStats])
async def get_database_stats(
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    stats = await service.get_database_stats()
    return ApiResponse(data=stats)


@router.get("/analytics", response_model=ApiResponse[AnalyticsOverview])
async def get_analytics(
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    analytics = await service.get_analytics()
    return ApiResponse(data=analytics)


@router.get("/health", response_model=ApiResponse[DatabaseHealth])
async def get_database_health(
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    health = await service.get_database_health()
    return ApiResponse(data=health)


@router.delete("/users/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    await service.delete_user(user_id, current_user.id)
    return ApiResponse(data={"deleted": True})


@router.get("/courses", response_model=ApiResponse[list[CourseListItem]])
async def get_all_courses(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    courses = await service.get_all_courses(skip, limit)
    return ApiResponse(data=courses)


@router.get("/courses/search", response_model=ApiResponse[list[CourseListItem]])
async def search_courses(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=50, ge=1, le=100),
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    courses = await service.search_courses(q, limit)
    return ApiResponse(data=courses)


@router.patch("/courses/{course_id}", response_model=ApiResponse[CourseListItem])
async def update_course(
    course_id: int,
    update_data: CourseUpdateRequest,
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    course = await service.update_course(
        course_id=course_id,
        title=update_data.title,
        department=update_data.department,
        ects=update_data.ects,
        description=update_data.description,
    )
    return ApiResponse(data=course)
