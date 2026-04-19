from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from nutrack.auth.dependencies import get_current_user
from nutrack.study.dependencies import get_study_service
from nutrack.study.schemas import (
    FlashcardItem,
    MockExamAttemptReviewResponse,
    MaterialUploadResponse,
    MockExamAttemptSessionResponse,
    MockExamAttemptResponse,
    MockExamCourseGroup,
    MockExamDashboardResponse,
    SaveMockExamAnswerRequest,
    SharedMaterialResponse,
)
from nutrack.study.service import StudyService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/study", tags=["study"])


@router.get(
    "/mock-exams",
    response_model=ApiResponse[list[MockExamCourseGroup]],
)
async def list_mock_exams(
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    exams = await service.list_mock_exams(user.id)
    return ApiResponse(data=exams)


@router.get(
    "/mock-exams/{mock_exam_id}/flashcards",
    response_model=ApiResponse[list[FlashcardItem]],
)
async def get_mock_exam_flashcards(
    mock_exam_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    flashcards = await service.get_mock_exam_flashcards(user.id, mock_exam_id)
    return ApiResponse(data=flashcards)


@router.get(
    "/mock-exams/{mock_exam_id}",
    response_model=ApiResponse[MockExamDashboardResponse],
)
async def get_mock_exam_dashboard(
    mock_exam_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    dashboard = await service.get_mock_exam_dashboard(user.id, mock_exam_id)
    return ApiResponse(data=dashboard)


@router.post(
    "/mock-exams/{mock_exam_id}/attempts",
    response_model=ApiResponse[MockExamAttemptResponse],
)
async def start_mock_exam_attempt(
    mock_exam_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    attempt = await service.start_mock_exam_attempt(user.id, mock_exam_id)
    return ApiResponse(data=attempt)


@router.get(
    "/mock-exams/attempts/{attempt_id}",
    response_model=ApiResponse[MockExamAttemptSessionResponse],
)
async def get_mock_exam_attempt(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    attempt = await service.get_mock_exam_attempt(user.id, attempt_id)
    return ApiResponse(data=attempt)


@router.get(
    "/mock-exams/attempts/{attempt_id}/review",
    response_model=ApiResponse[MockExamAttemptReviewResponse],
)
async def get_mock_exam_attempt_review(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    review = await service.get_mock_exam_attempt_review(user.id, attempt_id)
    return ApiResponse(data=review)


@router.put(
    "/mock-exams/attempts/{attempt_id}/answers/{link_id}",
    response_model=ApiResponse,
)
async def save_mock_exam_answer(
    attempt_id: int,
    link_id: int,
    body: SaveMockExamAnswerRequest,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    answer = await service.save_mock_exam_answer(
        user.id,
        attempt_id,
        link_id,
        body.selected_option_index,
    )
    return ApiResponse(data=answer)


@router.post(
    "/mock-exams/attempts/{attempt_id}/submit",
    response_model=ApiResponse[MockExamAttemptResponse],
)
async def submit_mock_exam_attempt(
    attempt_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    attempt = await service.submit_mock_exam_attempt(user.id, attempt_id)
    return ApiResponse(data=attempt)


@router.post(
    "/{course_id}/materials/uploads",
    response_model=ApiResponse[list[MaterialUploadResponse]],
    status_code=status.HTTP_201_CREATED,
)
async def upload_course_materials(
    course_id: int,
    week: int = Form(...),
    request_shared_library: bool = Form(default=False),
    files: list[UploadFile] = File(...),
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    uploads = await service.queue_uploads(
        user.id,
        course_id,
        week,
        request_shared_library,
        files,
    )
    return ApiResponse(data=uploads)


@router.get(
    "/{course_id}/materials/uploads",
    response_model=ApiResponse[list[MaterialUploadResponse]],
)
async def list_user_course_materials(
    course_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    uploads = await service.list_user_uploads(user.id, course_id)
    return ApiResponse(data=uploads)


@router.get(
    "/{course_id}/materials/library",
    response_model=ApiResponse[list[SharedMaterialResponse]],
)
async def list_shared_course_materials(
    course_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    materials = await service.list_shared_library(user.id, course_id)
    return ApiResponse(data=materials)


@router.delete(
    "/{course_id}/materials/uploads/{upload_id}",
    response_model=ApiResponse,
)
async def delete_user_course_material(
    course_id: int,
    upload_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    result = await service.delete_user_upload(user.id, course_id, upload_id)
    return ApiResponse(data=result)


@router.post(
    "/{course_id}/materials/uploads/{upload_id}/cancel-publish",
    response_model=ApiResponse[MaterialUploadResponse],
)
async def cancel_publish_course_material(
    course_id: int,
    upload_id: int,
    user: User = Depends(get_current_user),
    service: StudyService = Depends(get_study_service),
):
    upload = await service.cancel_user_publish(user.id, course_id, upload_id)
    return ApiResponse(data=upload)
