from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Schedule (existing)
# ---------------------------------------------------------------------------


class CourseSearchItem(BaseModel):
    id: int
    code: str
    level: str
    section: str | None = None
    title: str
    ects: int
    term: str
    year: int
    meeting_time: str | None = None
    room: str | None = None


class InvalidScheduleRow(BaseModel):
    row: int
    course_code: str | None = None
    course_name: str | None = None
    error: str


class CourseScheduleUploadResponse(BaseModel):
    term: str
    year: int
    processed_rows: int
    inserted_count: int
    updated_count: int
    invalid_rows_count: int = 0
    invalid_rows: list[InvalidScheduleRow] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Catalog
# ---------------------------------------------------------------------------


class SectionGpaStats(BaseModel):
    """GPA statistics for one section of a course in a given term/year."""

    section: str | None = None
    term: str
    year: int
    faculty: str | None = None
    avg_gpa: float | None = None
    total_enrolled: int | None = None
    grade_distribution: dict[str, float] = Field(default_factory=dict)


class ProfessorStats(BaseModel):
    """Aggregated stats for a single professor across all their sections."""

    faculty: str
    sections: list[SectionGpaStats] = Field(default_factory=list)
    avg_gpa: float | None = None
    total_enrolled: int = 0


class CourseOfferingInfo(BaseModel):
    """Schedule info for a single section offering."""

    section: str | None = None
    faculty: str | None = None
    meeting_time: str | None = None
    room: str | None = None
    days: str | None = None
    enrolled: int | None = None
    capacity: int | None = None
    term: str
    year: int


class CourseDetailResponse(BaseModel):
    """Full course record from the catalog, optionally annotated with GPA data."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    level: str
    title: str
    ects: int
    description: str | None = None
    prerequisites: str | None = None
    corequisites: str | None = None
    antirequisites: str | None = None
    priority_1: str | None = None
    priority_2: str | None = None
    priority_3: str | None = None
    priority_4: str | None = None
    school: str | None = None
    department: str | None = None
    academic_level: str | None = None
    credits_us: float | None = None
    pass_grade: str | None = None
    # Populated from course_gpa_stats when available
    avg_gpa: float | None = None
    total_enrolled: int | None = None
    # Terms the course has been offered in (e.g. ["Fall", "Spring"])
    terms_available: list[str] = Field(default_factory=list)
    # Per-section stats (populated only in detail endpoint)
    sections: list[SectionGpaStats] = Field(default_factory=list)
    # Professors grouped with their avg GPA (populated only in detail endpoint)
    professors: list[ProfessorStats] = Field(default_factory=list)
    # Schedule offerings from the most recent term (list in catalog, detail in course page)
    offerings: list[CourseOfferingInfo] = Field(default_factory=list)
    # Computed for authenticated user: eligibility and registration priority
    is_eligible: bool | None = None
    ineligibility_reason: str | None = None
    user_priority: int | None = None  # 1, 2, 3, 4 = has that priority; None = open / no priority


class InvalidCatalogRow(BaseModel):
    row: int
    course_code: str | None = None
    course_title: str | None = None
    error: str


class CourseCatalogUploadResponse(BaseModel):
    processed_rows: int
    inserted_count: int
    updated_count: int
    skipped_count: int = 0
    invalid_rows_count: int = 0
    invalid_rows: list[InvalidCatalogRow] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


class GradeCount(BaseModel):
    grade: str
    count: int
    percentage: float = Field(ge=0.0, le=100.0)


class CourseStatsResponse(BaseModel):
    course_id: int
    code: str
    level: str
    title: str
    total_enrollments: int
    total_distinct_students: int
    avg_gpa: float | None = None
    pass_rate: float | None = None
    withdraw_rate: float | None = None
    grade_distribution: list[GradeCount] = Field(default_factory=list)
    terms_offered: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# GPA stats upload
# ---------------------------------------------------------------------------


class InvalidGpaStatsRow(BaseModel):
    row: int | None = None
    line: int | None = None
    page: int | None = None
    error: str


class GpaStatsUploadResponse(BaseModel):
    term: str
    year: int
    processed_rows: int
    inserted_count: int
    updated_count: int
    invalid_rows_count: int = 0
    invalid_rows: list[InvalidGpaStatsRow] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Reviews
# ---------------------------------------------------------------------------


class ReviewCreate(BaseModel):
    comment: str | None = Field(default=None, max_length=2000)
    overall_rating: int = Field(ge=1, le=5)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    informativeness: int | None = Field(default=None, ge=1, le=5)
    gpa_boost: int | None = Field(default=None, ge=1, le=5)
    workload: int | None = Field(default=None, ge=1, le=5)


class ReviewUpdate(BaseModel):
    comment: str | None = Field(default=None, max_length=2000)
    overall_rating: int | None = Field(default=None, ge=1, le=5)
    difficulty: int | None = Field(default=None, ge=1, le=5)
    informativeness: int | None = Field(default=None, ge=1, le=5)
    gpa_boost: int | None = Field(default=None, ge=1, le=5)
    workload: int | None = Field(default=None, ge=1, le=5)


class ReviewAuthor(BaseModel):
    id: int
    first_name: str
    last_name: str


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    course_id: int
    user_id: int
    author: ReviewAuthor
    comment: str | None
    overall_rating: int
    difficulty: int | None
    informativeness: int | None
    gpa_boost: int | None
    workload: int | None
    created_at: datetime
    updated_at: datetime


class ReviewStats(BaseModel):
    total: int
    avg_overall_rating: float | None = None
    avg_difficulty: float | None = None
    avg_informativeness: float | None = None
    avg_gpa_boost: float | None = None
    avg_workload: float | None = None


class ReviewsPage(BaseModel):
    stats: ReviewStats
    reviews: list[ReviewResponse]


# ---------------------------------------------------------------------------
# Requirements upload
# ---------------------------------------------------------------------------


class RequirementsUploadResponse(BaseModel):
    processed_rows: int
    updated_count: int
    not_found_count: int
    skipped_count: int
    lower_priority_count: int = 0
    error_count: int = 0


# ---------------------------------------------------------------------------
# Eligibility
# ---------------------------------------------------------------------------


class PrerequisiteCheck(BaseModel):
    course_code: str
    required_grade: str | None = None
    met: bool
    your_grade: str | None = None


class CorequisiteCheck(BaseModel):
    course_code: str
    met: bool
    your_grade: str | None = None
    your_status: str | None = None


class AntirequisiteCheck(BaseModel):
    course_code: str
    blocking: bool  # True if user has already passed this course
    your_grade: str | None = None


class EligibilityResponse(BaseModel):
    course_id: int
    can_register: bool
    prerequisites_met: bool
    corequisites_met: bool
    antirequisites_blocking: bool = False
    prerequisite_checks: list[PrerequisiteCheck] = Field(default_factory=list)
    corequisite_checks: list[CorequisiteCheck] = Field(default_factory=list)
    antirequisite_checks: list[AntirequisiteCheck] = Field(default_factory=list)
