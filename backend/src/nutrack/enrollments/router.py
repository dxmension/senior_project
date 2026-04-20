from fastapi import APIRouter, Depends, Query, status

from nutrack.auth.dependencies import get_current_user
from nutrack.enrollments.dependencies import get_enrollment_service
from nutrack.enrollments.models import EnrollmentStatus
from nutrack.enrollments.schemas import (
    CreateEnrollmentRequest,
    DeleteEnrollmentResponse,
    EnrollmentItemResponse,
)
from nutrack.enrollments.service import EnrollmentService
from nutrack.utils import ApiResponse
from nutrack.users.models import User

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("", response_model=ApiResponse[list[EnrollmentItemResponse]])
async def list_enrollments(
    status_filter: EnrollmentStatus | None = Query(
        default=None,
        alias="status",
    ),
    user: User = Depends(get_current_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    enrollments = await service.list_enrollments(user.id, status_filter)
    return ApiResponse(data=enrollments)


@router.post(
    "",
    response_model=ApiResponse[EnrollmentItemResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_enrollment(
    body: CreateEnrollmentRequest,
    user: User = Depends(get_current_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    enrollment = await service.create_manual_enrollment(
        user.id, body.course_id, body.course_overload_acknowledged
    )
    return ApiResponse(data=enrollment)


@router.delete(
    "/{course_id}",
    response_model=ApiResponse[DeleteEnrollmentResponse],
)
async def delete_enrollment(
    course_id: int,
    term: str = Query(..., min_length=1),
    year: int = Query(..., ge=2000),
    user: User = Depends(get_current_user),
    service: EnrollmentService = Depends(get_enrollment_service),
):
    await service.delete_enrollment(user.id, course_id, term, year)
    return ApiResponse(data=DeleteEnrollmentResponse(deleted=True))
