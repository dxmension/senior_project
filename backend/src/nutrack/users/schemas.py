from datetime import datetime

from pydantic import BaseModel, ConfigDict
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
    created_at: datetime


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    major: str | None = None
    kazakh_level: str | None = None
    study_year: int | None = None
    avatar_url: str | None = None


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
