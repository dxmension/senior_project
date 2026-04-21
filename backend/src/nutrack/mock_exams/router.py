from fastapi import APIRouter, Depends, Query

from nutrack.auth.dependencies import get_current_user
from nutrack.mock_exams.dependencies import get_mock_exam_service
from nutrack.mock_exams.schemas import (
    CurateQuestionRequest,
    MockExamAttemptResponse,
    MockExamAttemptReviewResponse,
    MockExamAttemptSessionResponse,
    MockExamCourseGroup,
    MockExamDashboardResponse,
    SaveMockExamAnswerRequest,
    UserSubmitQuestionRequest,
    UserSubmittedQuestionResponse,
)
from nutrack.mock_exams.service import MockExamService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/mock-exams", tags=["mock_exams"])


@router.get("", response_model=ApiResponse[list[MockExamCourseGroup]])
async def list_mock_exams(
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    exams = await service.list_mock_exams(user.id)
    return ApiResponse(data=exams)


@router.get("/{mock_exam_id}", response_model=ApiResponse[MockExamDashboardResponse])
async def get_mock_exam_dashboard(
    mock_exam_id: int,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    dashboard = await service.get_mock_exam_dashboard(user.id, mock_exam_id)
    return ApiResponse(data=dashboard)


@router.post(
    "/{mock_exam_id}/attempts",
    response_model=ApiResponse[MockExamAttemptResponse],
)
async def start_mock_exam_attempt(
    mock_exam_id: int,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    attempt = await service.start_mock_exam_attempt(user.id, mock_exam_id)
    return ApiResponse(data=attempt)


@router.get(
    "/attempts/{attempt_id}",
    response_model=ApiResponse[MockExamAttemptSessionResponse],
)
async def get_mock_exam_attempt(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    attempt = await service.get_mock_exam_attempt(user.id, attempt_id)
    return ApiResponse(data=attempt)


@router.get(
    "/attempts/{attempt_id}/review",
    response_model=ApiResponse[MockExamAttemptReviewResponse],
)
async def get_mock_exam_attempt_review(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    review = await service.get_mock_exam_attempt_review(user.id, attempt_id)
    return ApiResponse(data=review)


@router.put("/attempts/{attempt_id}/answers/{link_id}", response_model=ApiResponse)
async def save_mock_exam_answer(
    attempt_id: int,
    link_id: int,
    body: SaveMockExamAnswerRequest,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    answer = await service.save_mock_exam_answer(
        user.id,
        attempt_id,
        link_id,
        body.selected_option_index,
    )
    return ApiResponse(data=answer)


@router.post(
    "/attempts/{attempt_id}/submit",
    response_model=ApiResponse[MockExamAttemptResponse],
)
async def submit_mock_exam_attempt(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    attempt = await service.submit_mock_exam_attempt(user.id, attempt_id)
    return ApiResponse(data=attempt)


@router.post(
    "/questions/submit",
    response_model=ApiResponse[UserSubmittedQuestionResponse],
)
async def submit_question(
    body: UserSubmitQuestionRequest,
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    question = await service.submit_question(user.id, body)
    return ApiResponse(data=question)


@router.get(
    "/questions/my-submissions",
    response_model=ApiResponse[list[UserSubmittedQuestionResponse]],
)
async def list_my_submissions(
    course_id: int = Query(..., ge=1),
    user: User = Depends(get_current_user),
    service: MockExamService = Depends(get_mock_exam_service),
):
    questions = await service.list_user_submissions(user.id, course_id)
    return ApiResponse(data=questions)
