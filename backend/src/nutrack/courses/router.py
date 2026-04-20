from fastapi import APIRouter, Depends, File, Query, UploadFile, status

from nutrack.auth.dependencies import get_current_admin_user, get_current_user
from nutrack.courses.dependencies import (
    get_course_catalog_service,
    get_course_eligibility_service,
    get_course_gpa_stats_service,
    get_course_requirements_service,
    get_course_review_service,
    get_course_schedule_service,
    get_course_search_service,
    get_course_stats_service,
    get_recommendation_service,
)
from nutrack.courses.recommendation_service import CourseRecommendationService
from nutrack.courses.schemas import (
    CourseDetailResponse,
    CourseScheduleUploadResponse,
    CourseSearchItem,
    CourseStatsResponse,
    DescriptionsUploadResponse,
    EligibilityResponse,
    GpaStatsUploadResponse,
    RecommendationsResponse,
    RequirementsUploadResponse,
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
    ReviewsPage,
)
from nutrack.courses.service import (
    CourseCatalogService,
    CourseEligibilityService,
    CourseGpaStatsService,
    CourseRequirementsService,
    CourseReviewService,
    CourseScheduleService,
    CourseSearchService,
    CourseStatsService,
)
from nutrack.utils import ApiResponse
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


@router.get("/recommended", response_model=ApiResponse[RecommendationsResponse])
async def get_recommended_courses(
    current_user: User = Depends(get_current_user),
    service: CourseRecommendationService = Depends(get_recommendation_service),
):
    result = await service.get_recommendations(current_user)
    return ApiResponse(data=result)


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
    department: str | None = Query(default=None, description="Filter by department (partial match)"),
    school: str | None = Query(default=None, description="Filter by school (partial match)"),
    academic_level: str | None = Query(default=None, description="Filter by academic level, e.g. Undergraduate"),
    term: str | None = Query(default=None, description="Filter by term availability, e.g. Fall, Spring, Summer"),
    level_prefix: str | None = Query(default=None, description="Filter by course level prefix: '1' for 100-level, '2' for 200-level, etc."),
    eligible_only: bool = Query(default=False, description="Only return courses the user is eligible for"),
    has_priority: bool = Query(default=False, description="Only return courses where the user has a registration priority"),
    min_gpa: float | None = Query(default=None, ge=0.0, le=4.0, description="Minimum average GPA (e.g. 2.5)"),
    min_rating: float | None = Query(default=None, ge=1.0, le=5.0, description="Minimum average review rating (1–5)"),
    current_user: User = Depends(get_current_user),
    service: CourseCatalogService = Depends(get_course_catalog_service),
):
    user_major = getattr(current_user, "major", None)
    user_kazakh_level = getattr(current_user, "kazakh_level", None)
    params = {
        "skip": skip,
        "limit": limit,
        "search": q,
        "user_id": current_user.id,
    }
    if user_major is not None:
        params["user_major"] = user_major
    if user_kazakh_level is not None:
        params["kazakh_level"] = user_kazakh_level
    optional_params = {
        "department": department,
        "school": school,
        "academic_level": academic_level,
        "term": term,
        "level_prefix": level_prefix,
    }
    for key, value in optional_params.items():
        if value is not None:
            params[key] = value
    if eligible_only:
        params["eligible_only"] = True
    if has_priority:
        params["has_priority"] = True
    if min_gpa is not None:
        params["min_gpa"] = min_gpa
    if min_rating is not None:
        params["min_rating"] = min_rating

    courses, total = await service.list_courses(**params)
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
# Descriptions upload
# ---------------------------------------------------------------------------


@router.post(
    "/catalog/descriptions/upload",
    response_model=ApiResponse[DescriptionsUploadResponse],
    status_code=status.HTTP_200_OK,
    summary="Bulk-update course descriptions from a JSON file — admin only",
)
async def upload_descriptions(
    file: UploadFile = File(...),
    _: User = Depends(get_current_admin_user),
    service: CourseCatalogService = Depends(get_course_catalog_service),
):
    """
    Accepts the JSON file produced by export_courses.py (or any JSON array of
    {code, level, description} objects).  Only entries with a non-empty
    description are applied; entries not found in the catalog are skipped.
    """
    result = await service.upload_descriptions(file)
    return ApiResponse(data=result)


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


# ---------------------------------------------------------------------------
# Requirements upload
# ---------------------------------------------------------------------------


@router.post(
    "/requirements/upload",
    response_model=ApiResponse[RequirementsUploadResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Upload Course Requirements PDF to update prerequisites/corequisites — admin only",
)
async def upload_course_requirements(
    file: UploadFile = File(...),
    term: str = Query(..., min_length=1, description="Semester term, e.g. Fall"),
    year: int = Query(..., ge=2000, description="Semester year, e.g. 2026"),
    _: User = Depends(get_current_admin_user),
    service: CourseRequirementsService = Depends(get_course_requirements_service),
):
    """
    Accepts the Course Requirements and Registration Priorities PDF.
    Parses prerequisite and corequisite columns and upserts them into
    the courses table.  The course catalog must already be uploaded.
    """
    result = await service.upload(file, term, year)
    return ApiResponse(data=result)


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------


@router.get(
    "/catalog/{course_id}/eligibility",
    response_model=ApiResponse[EligibilityResponse],
    summary="Check if the current user can register for a course",
)
async def check_eligibility(
    course_id: int,
    current_user: User = Depends(get_current_user),
    service: CourseEligibilityService = Depends(get_course_eligibility_service),
):
    """
    Returns whether the authenticated user satisfies all prerequisites
    (must be PASSED with the required grade) and corequisites
    (must be PASSED or IN_PROGRESS) for the given course.
    """
    result = await service.check_eligibility(
        course_id, current_user.id, getattr(current_user, "kazakh_level", None)
    )
    return ApiResponse(data=result)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


@router.get(
    "/catalog/{course_id}/reviews",
    response_model=ApiResponse[ReviewsPage],
    summary="List reviews for a course",
)
async def list_reviews(
    course_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    _: User = Depends(get_current_user),
    service: CourseReviewService = Depends(get_course_review_service),
):
    page = await service.list_reviews(course_id, skip, limit)
    return ApiResponse(data=page)


@router.post(
    "/catalog/{course_id}/reviews",
    response_model=ApiResponse[ReviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review for a course",
)
async def create_review(
    course_id: int,
    body: ReviewCreate,
    current_user: User = Depends(get_current_user),
    service: CourseReviewService = Depends(get_course_review_service),
):
    review = await service.create_review(course_id, current_user.id, body)
    return ApiResponse(data=review)


@router.put(
    "/catalog/{course_id}/reviews/{review_id}",
    response_model=ApiResponse[ReviewResponse],
    summary="Update your review for a course",
)
async def update_review(
    course_id: int,
    review_id: int,
    body: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    service: CourseReviewService = Depends(get_course_review_service),
):
    review = await service.update_review(course_id, review_id, current_user.id, body)
    return ApiResponse(data=review)


@router.delete(
    "/catalog/{course_id}/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete your review for a course",
)
async def delete_review(
    course_id: int,
    review_id: int,
    current_user: User = Depends(get_current_user),
    service: CourseReviewService = Depends(get_course_review_service),
):
    await service.delete_review(course_id, review_id, current_user.id)
