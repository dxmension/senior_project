from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from nutrack.auth.dependencies import get_current_admin_user, get_current_user
from nutrack.courses.dependencies import (
    get_course_catalog_service,
    get_course_gpa_stats_service,
    get_course_schedule_service,
    get_course_search_service,
    get_course_stats_service,
)
from nutrack.courses.schemas import (
    CourseDetailResponse,
    CourseScheduleUploadResponse,
    CourseSearchItem,
    CourseStatsResponse,
    GpaStatsUploadResponse,
)
from nutrack.courses.service import (
    CourseCatalogService,
    CourseGpaStatsService,
    CourseScheduleService,
    CourseSearchService,
    CourseStatsService,
)
from nutrack.shared.api.response import ApiResponse
from nutrack.users.models import User

router = APIRouter(prefix="/courses", tags=["courses"])


# ---------------------------------------------------------------------------
# Schedule (semester timetable)
# ---------------------------------------------------------------------------


@router.get("", response_model=ApiResponse[list[CourseSearchItem]])
async def search_courses(
    q: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=20),
    term: str | None = Query(default=None),
    year: int | None = Query(default=None, ge=2000),
    _: User = Depends(get_current_user),
    service: CourseSearchService = Depends(get_course_search_service),
):
    # CourseSearchService raises CourseSearchError (AppException) on invalid
    # term/year — handled by the global app_exception_handler, no try/except here.
    courses = await service.search_courses(q, limit, term, year)
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
    result = await service.ingest(file, term, year)
    return ApiResponse(data=CourseScheduleUploadResponse(**result))


# ---------------------------------------------------------------------------
# Catalog (persistent course definitions)
# ---------------------------------------------------------------------------



@router.get(
    "/catalog",
    response_model=ApiResponse[list[CourseDetailResponse]],
    summary="List all courses in catalog",
)
async def list_catalog(
    q: str | None = Query(default=None, description="Search by code, title, department"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(get_current_user),
    service: CourseCatalogService = Depends(get_course_catalog_service),
):
    courses, total = await service.list_courses(skip=skip, limit=limit, search=q)
    return ApiResponse(data=courses, meta={"total": total, "skip": skip, "limit": limit})


@router.get(
    "/catalog/{course_id}",
    response_model=ApiResponse[CourseDetailResponse],
    summary="Get course detail by ID",
)
async def get_course(
    course_id: int,
    _: User = Depends(get_current_user),
    service: CourseCatalogService = Depends(get_course_catalog_service),
):
    course = await service.get_course(course_id)
    return ApiResponse(data=course)


@router.get(
    "/catalog/{course_id}/stats",
    response_model=ApiResponse[CourseStatsResponse],
    summary="Aggregate stats for a course (avg GPA, pass rate, grade distribution)",
)
async def get_course_stats(
    course_id: int,
    _: User = Depends(get_current_user),
    service: CourseStatsService = Depends(get_course_stats_service),
):
    """
    Returns statistics computed live from the enrollments table:
    - avg_gpa: average grade points across all students who received a grade
    - pass_rate: % of enrollments with status=passed
    - withdraw_rate: % of enrollments with status=withdrawn
    - grade_distribution: count + percentage per grade letter (A, A-, B+, ...)
    - terms_offered: list of "Spring 2024", "Fall 2023", etc.
    """
    stats = await service.get_stats(course_id)
    return ApiResponse(data=stats)


# ---------------------------------------------------------------------------
# GPA stats upload
# ---------------------------------------------------------------------------


@router.post(
    "/gpa-stats/upload",
    response_model=ApiResponse[GpaStatsUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload GPA statistics PDF for a semester — admin only",
)
async def upload_gpa_stats(
    file: UploadFile = File(...),
    term: str = Query(..., min_length=1, description="Semester term, e.g. Fall"),
    year: int = Query(..., ge=2000, description="Semester year, e.g. 2025"),
    _: User = Depends(get_current_admin_user),
    service: CourseGpaStatsService = Depends(get_course_gpa_stats_service),
):
    """
    Accepts a PDF report exported from the NU GPA statistics system.
    Upserts per-course GPA data (avg_gpa, total_enrolled, grade_distribution)
    into course_gpa_stats for the given term/year.

    The course catalog must be uploaded first — rows for unknown courses are skipped.
    """
    result = await service.upload(file, term, year)
    return ApiResponse(data=result)
