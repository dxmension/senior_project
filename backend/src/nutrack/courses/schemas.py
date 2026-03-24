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
    school: str | None = None
    department: str | None = None
    academic_level: str | None = None
    credits_us: float | None = None
    pass_grade: str | None = None
    # Populated from course_gpa_stats when available
    avg_gpa: float | None = None
    total_enrolled: int | None = None


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
    row: int
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
