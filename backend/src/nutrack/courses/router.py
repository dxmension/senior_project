from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from nutrack.auth.dependencies import get_current_admin_user, get_current_user
from nutrack.courses.dependencies import (
    get_course_schedule_service,
    get_course_search_service,
)
from nutrack.courses.schemas import CourseScheduleUploadResponse, CourseSearchItem
from nutrack.courses.service import CourseScheduleService, CourseSearchService
from nutrack.shared.api.response import ApiResponse
from nutrack.users.models import User

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=ApiResponse[list[CourseSearchItem]])
async def search_courses(
    q: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=20),
    term: str | None = Query(default=None),
    year: int | None = Query(default=None, ge=2000),
    _: User = Depends(get_current_user),
    service: CourseSearchService = Depends(get_course_search_service),
):
    try:
        courses = await service.search_courses(q, limit, term, year)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(data=courses)


@router.post(
    "/schedule/upload",
    response_model=ApiResponse[CourseScheduleUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_course_schedule(
    file: UploadFile = File(...),
    term: str = Query(..., min_length=1),
    year: int = Query(..., ge=2000),
    _: User = Depends(get_current_admin_user),
    service: CourseScheduleService = Depends(get_course_schedule_service),
):
    try:
        result = await service.ingest(file, term, year)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return ApiResponse(data=CourseScheduleUploadResponse(**result))
