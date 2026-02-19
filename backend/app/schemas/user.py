from datetime import datetime

from pydantic import BaseModel


class UserProfileResponse(BaseModel):
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
    created_at: datetime

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    major: str | None = None
    study_year: int | None = None
    avatar_url: str | None = None


class EnrollmentResponse(BaseModel):
    id: int
    course_code: str
    course_title: str
    ects: int
    grade: str | None = None
    grade_points: float | None = None
    semester: str
    status: str

    class Config:
        from_attributes = True


class CreditsBySemester(BaseModel):
    semester: str
    term: int
    credits: int


class UserStatsResponse(BaseModel):
    total_credits: int
    completed_courses: int
    current_gpa: float | None = None
    semesters_completed: int
    credits_by_semester: list[CreditsBySemester] = []
