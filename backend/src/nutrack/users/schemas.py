from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from nutrack.enrollments.schemas import EnrollmentItemResponse

EnrollmentResponse = EnrollmentItemResponse


class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    first_name: str
    last_name: str
    avatar_url: str | None = None
    major: str | None = None
    kazakh_level: str | None = None
    study_year: int | None = None
    enrollment_year: int | None = None
    cgpa: float | None = None
    total_credits_earned: int | None = None
    total_credits_enrolled: int | None = None
    is_onboarded: bool
    is_admin: bool = False
    subscribed_to_notifications: bool = True
    created_at: datetime


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    major: str | None = None
    kazakh_level: str | None = None
    study_year: int | None = None
    avatar_url: str | None = None
    subscribed_to_notifications: bool | None = None


class CreditsBySemester(BaseModel):
    semester: str
    term: str
    year: int
    credits: int


class UserStatsResponse(BaseModel):
    total_credits: int
    completed_courses: int
    current_gpa: float | None = None
    semesters_completed: int
    credits_by_semester: list[CreditsBySemester] = []


class MatchedCourseResponse(BaseModel):
    code: str
    status: str


class RequirementResultResponse(BaseModel):
    name: str
    required_count: int
    completed_count: int
    in_progress_count: int
    status: str  # "completed" | "in_progress" | "missing"
    matched_courses: list[MatchedCourseResponse]
    ects_per_course: int
    note: str
    terms_available: list[str] = Field(default_factory=list)


class CategoryResultResponse(BaseModel):
    name: str
    requirements: list[RequirementResultResponse]
    total_ects: int
    completed_ects: int


class AuditResultResponse(BaseModel):
    major: str
    supported: bool
    total_ects: int
    completed_ects: int
    in_progress_ects: int
    actual_credits_earned: int
    categories: list[CategoryResultResponse]


class SuggestedCourseResponse(BaseModel):
    code: str
    level: str
    full_code: str
    title: str
    ects: int
    user_priority: int | None
    terms_offered: list[str]


class PlannedCourseResponse(BaseModel):
    requirement_name: str
    category: str
    ects: int
    note: str
    terms_available: list[str]
    status: str  # "in_progress" | "pending"
    is_elective: bool = False
    depends_on: str | None = None
    matched_codes: list[str] = []  # in_progress: enrolled course codes; used for course lookup
    suggested_courses: list[SuggestedCourseResponse] = []


class PlannedTermResponse(BaseModel):
    term: str
    year: int
    label: str
    courses: list[PlannedCourseResponse]
    total_ects: int
    is_current: bool
    study_year: int | None = None


class DegreePlanResponse(BaseModel):
    major: str
    graduation_term: str | None
    graduation_year: int | None
    needs_extra_time: bool
    enrollment_year: int | None
    terms: list[PlannedTermResponse]
