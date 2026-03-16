from fastapi import APIRouter, Depends, File, UploadFile, status

from nutrack.auth.dependencies import get_current_admin_user
from nutrack.courses.dependencies import get_course_schedule_service
from nutrack.courses.schemas import CourseScheduleUploadResponse
from nutrack.courses.service import CourseScheduleService
from nutrack.shared.api.response import ApiResponse
from nutrack.users.models import User

router = APIRouter(prefix="/courses", tags=["courses"])


@router.post(
    "/schedule/upload",
    response_model=ApiResponse[CourseScheduleUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_course_schedule(
    file: UploadFile = File(...),
    _: User = Depends(get_current_admin_user),
    service: CourseScheduleService = Depends(get_course_schedule_service),
):
    result = await service.ingest(file)
    return ApiResponse(data=CourseScheduleUploadResponse(**result))
