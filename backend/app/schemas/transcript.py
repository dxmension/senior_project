from datetime import datetime

from pydantic import BaseModel

from app.models.transcript import TranscriptStatus


class CourseRecord(BaseModel):
    code: str
    title: str
    semester: str
    term: int
    grade: str
    grade_points: float
    ects: int


class ParsedTranscriptData(BaseModel):
    major: str | None = None
    gpa: float | None = None
    total_credits_earned: int | None = None
    total_credits_enrolled: int | None = None
    courses: list[CourseRecord] = []


class TranscriptStatusResponse(BaseModel):
    id: int
    status: TranscriptStatus
    major: str | None = None
    gpa: float | None = None
    total_credits_earned: int | None = None
    total_credits_enrolled: int | None = None
    parsed_data: dict | None = None
    error_message: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class TranscriptConfirmRequest(BaseModel):
    major: str | None = None
    courses: list[CourseRecord]


class ManualTranscriptRequest(BaseModel):
    major: str | None = None
    courses: list[CourseRecord]
