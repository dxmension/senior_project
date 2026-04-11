from datetime import datetime

from pydantic import BaseModel


class UserListItem(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    major: str | None
    study_year: int | None
    cgpa: float | None
    is_onboarded: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdateRequest(BaseModel):
    is_admin: bool | None = None
    is_onboarded: bool | None = None
    major: str | None = None
    study_year: int | None = None


class DatabaseStats(BaseModel):
    total_users: int
    total_courses: int
    total_enrollments: int


class AnalyticsOverview(BaseModel):
    total_users: int
    active_users_last_30_days: int
    total_courses: int
    total_course_offerings: int
    total_enrollments: int
    users_by_study_year: dict[int, int]
    users_by_major: dict[str, int]


class UserDetail(BaseModel):
    id: int
    email: str
    google_id: str
    first_name: str
    last_name: str
    major: str | None
    study_year: int | None
    cgpa: float | None
    total_credits_earned: int | None
    total_credits_enrolled: int | None
    avatar_url: str | None
    is_onboarded: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime
    enrollment_count: int

    class Config:
        from_attributes = True


class DatabaseHealth(BaseModel):
    database_connected: bool
    redis_connected: bool
    database_size_mb: float | None


class CourseListItem(BaseModel):
    id: int
    code: str
    level: str
    title: str
    ects: int
    department: str | None
    school: str | None

    class Config:
        from_attributes = True


class CourseUpdateRequest(BaseModel):
    title: str | None = None
    department: str | None = None
    ects: int | None = None
    description: str | None = None
