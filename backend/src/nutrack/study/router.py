from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from nutrack.auth.dependencies import get_current_user
from nutrack.study.dependencies import get_study_service
from nutrack.study.schemas import MaterialUploadResponse, SharedMaterialResponse
from nutrack.study.service import StudyService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/study", tags=["study"])


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
