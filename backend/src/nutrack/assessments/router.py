from fastapi import APIRouter, Depends, Query, status

from nutrack.assessments.dependencies import get_assessment_service
from nutrack.assessments.schemas import (
    AssessmentResponse,
    CreateAssessmentRequest,
    UpdateAssessmentRequest,
)
from nutrack.assessments.service import AssessmentService
from nutrack.auth.dependencies import get_current_user
from nutrack.utils import ApiResponse
from nutrack.users.models import User

router = APIRouter(tags=["assessments"])


@router.get("", response_model=ApiResponse[list[AssessmentResponse]])
async def list_assessments(
    course_id: int | None = Query(default=None),
    upcoming_only: bool = Query(default=False),
    completed: bool | None = Query(default=None),
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    assessments = await service.list_assessments(
        user.id,
        course_id=course_id,
        upcoming_only=upcoming_only,
        completed=completed,
    )
    return ApiResponse(data=assessments)


@router.post(
    "",
    response_model=ApiResponse[AssessmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_assessment(
    body: CreateAssessmentRequest,
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    assessment = await service.create_assessment(user.id, body)
    return ApiResponse(data=assessment)


@router.get("/{assessment_id}", response_model=ApiResponse[AssessmentResponse])
async def get_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    assessment = await service.get_assessment(user.id, assessment_id)
    return ApiResponse(data=assessment)


@router.patch("/{assessment_id}", response_model=ApiResponse[AssessmentResponse])
async def update_assessment(
    assessment_id: int,
    body: UpdateAssessmentRequest,
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    assessment = await service.update_assessment(user.id, assessment_id, body)
    return ApiResponse(data=assessment)


@router.delete("/{assessment_id}", response_model=ApiResponse[None])
async def delete_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    await service.delete_assessment(user.id, assessment_id)
    return ApiResponse(data=None)
