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
from nutrack.study.dependencies import get_study_service
from nutrack.study.models import MaterialCurationStatus, MaterialUploadStatus
from nutrack.study.schemas import (
    AdminCourseOfferingResponse,
    AdminMockExamListItem,
    AdminMaterialUploadResponse,
    CreateMockExamQuestionRequest,
    CreateMockExamRequest,
    MaterialUploadResponse,
    MockExamAdminDetailResponse,
    MockExamQuestionAdminResponse,
    PublishMaterialRequest,
    SharedMaterialResponse,
    UpdateMockExamQuestionRequest,
    UpdateMockExamRequest,
)
from nutrack.study.service import StudyService
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


@router.get(
    "/courses/{course_id}/offerings",
    response_model=ApiResponse[list[AdminCourseOfferingResponse]],
)
async def list_course_offerings(
    course_id: int,
    _: User = Depends(get_current_admin_user),
    service: AdminService = Depends(get_admin_service),
):
    offerings = await service.list_course_offerings(course_id)
    return ApiResponse(data=offerings)


@router.get(
    "/materials/uploads",
    response_model=ApiResponse[list[AdminMaterialUploadResponse]],
)
async def list_material_uploads(
    course_id: int | None = Query(default=None, ge=1),
    user_id: int | None = Query(default=None, ge=1),
    upload_status: MaterialUploadStatus | None = Query(default=None),
    curation_status: MaterialCurationStatus | None = Query(default=None),
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    uploads = await service.list_admin_uploads(
        course_id=course_id,
        user_id=user_id,
        upload_status=upload_status,
        curation_status=curation_status,
    )
    return ApiResponse(data=uploads)


@router.post(
    "/materials/uploads/{upload_id}/publish",
    response_model=ApiResponse[SharedMaterialResponse],
)
async def publish_material_upload(
    upload_id: int,
    body: PublishMaterialRequest,
    admin: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    entry = await service.publish_upload(
        admin.id,
        upload_id,
        body.title,
        body.week,
    )
    return ApiResponse(data=entry)


@router.post("/materials/uploads/{upload_id}/reject", response_model=ApiResponse)
async def reject_material_upload(
    upload_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    result = await service.reject_upload(upload_id)
    return ApiResponse(data=result)


@router.post(
    "/materials/uploads/{upload_id}/unpublish",
    response_model=ApiResponse[MaterialUploadResponse],
)
async def unpublish_material_upload(
    upload_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    upload = await service.unpublish_upload(upload_id)
    return ApiResponse(data=upload)


@router.delete("/materials/uploads/{upload_id}", response_model=ApiResponse)
async def delete_material_upload(
    upload_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    result = await service.delete_upload(upload_id)
    return ApiResponse(data=result)


@router.get(
    "/mock-exams",
    response_model=ApiResponse[list[AdminMockExamListItem]],
)
async def list_admin_mock_exams(
    course_id: int = Query(..., ge=1),
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    exams = await service.list_admin_mock_exams(course_id)
    return ApiResponse(data=exams)


@router.get(
    "/mock-exams/{mock_exam_id}",
    response_model=ApiResponse[MockExamAdminDetailResponse],
)
async def get_admin_mock_exam_detail(
    mock_exam_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    exam = await service.get_admin_mock_exam_detail(mock_exam_id)
    return ApiResponse(data=exam)


@router.post(
    "/mock-exams",
    response_model=ApiResponse[MockExamAdminDetailResponse],
)
async def create_admin_mock_exam(
    body: CreateMockExamRequest,
    admin: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    exam = await service.create_mock_exam(admin.id, body)
    return ApiResponse(data=exam)


@router.patch(
    "/mock-exams/{mock_exam_id}",
    response_model=ApiResponse[MockExamAdminDetailResponse],
)
async def update_admin_mock_exam(
    mock_exam_id: int,
    body: UpdateMockExamRequest,
    admin: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    exam = await service.update_mock_exam(admin.id, mock_exam_id, body)
    return ApiResponse(data=exam)


@router.post("/mock-exams/{mock_exam_id}/deactivate", response_model=ApiResponse)
async def deactivate_admin_mock_exam(
    mock_exam_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    result = await service.deactivate_mock_exam(mock_exam_id)
    return ApiResponse(data=result)


@router.delete("/mock-exams/{mock_exam_id}", response_model=ApiResponse)
async def delete_admin_mock_exam(
    mock_exam_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    result = await service.delete_mock_exam(mock_exam_id)
    return ApiResponse(data=result)


@router.get(
    "/mock-exam-questions",
    response_model=ApiResponse[list[MockExamQuestionAdminResponse]],
)
async def list_admin_mock_exam_questions(
    course_id: int = Query(..., ge=1),
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    questions = await service.list_admin_mock_exam_questions(course_id)
    return ApiResponse(data=questions)


@router.post(
    "/mock-exam-questions",
    response_model=ApiResponse[MockExamQuestionAdminResponse],
)
async def create_admin_mock_exam_question(
    body: CreateMockExamQuestionRequest,
    admin: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    question = await service.create_mock_exam_question(admin.id, body)
    return ApiResponse(data=question)


@router.patch(
    "/mock-exam-questions/{question_id}",
    response_model=ApiResponse[MockExamQuestionAdminResponse],
)
async def update_admin_mock_exam_question(
    question_id: int,
    body: UpdateMockExamQuestionRequest,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    question = await service.update_mock_exam_question(question_id, body)
    return ApiResponse(data=question)


@router.delete("/mock-exam-questions/{question_id}", response_model=ApiResponse)
async def delete_admin_mock_exam_question(
    question_id: int,
    _: User = Depends(get_current_admin_user),
    service: StudyService = Depends(get_study_service),
):
    result = await service.delete_mock_exam_question(question_id)
    return ApiResponse(data=result)
