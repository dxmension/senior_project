from fastapi import APIRouter, Body, Depends, Query, status

from nutrack.assessments.dependencies import get_assessment_service
from nutrack.assessments.schemas import (
    AssessmentResponse,
    CreateAssessmentRequest,
    GenerateMockExamRequest,
    MockExamGenerationQueuedResponse,
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


@router.post(
    "/{assessment_id}/generate-mock-exam",
    response_model=ApiResponse[MockExamGenerationQueuedResponse],
)
async def generate_mock_exam(
    assessment_id: int,
    body: GenerateMockExamRequest = Body(default_factory=GenerateMockExamRequest),
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    job = await service.generate_mock_exam(
        user.id,
        assessment_id,
        difficulty=body.difficulty,
        question_count=body.question_count,
        selected_upload_ids=body.selected_upload_ids,
        selected_shared_material_ids=body.selected_shared_material_ids,
        include_rumored_questions=body.include_rumored_questions,
        include_historic_questions=body.include_historic_questions,
    )
    return ApiResponse(data=job)


@router.delete("/{assessment_id}", response_model=ApiResponse[None])
async def delete_assessment(
    assessment_id: int,
    user: User = Depends(get_current_user),
    service: AssessmentService = Depends(get_assessment_service),
):
    await service.delete_assessment(user.id, assessment_id)
    return ApiResponse(data=None)
