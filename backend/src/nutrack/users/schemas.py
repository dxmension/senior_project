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
    study_year: int | None = None
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
