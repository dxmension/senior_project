from pydantic import BaseModel


class TranscriptUploadResponse(BaseModel):
    upload_id: str
    status: str


class TranscriptUploadStatusResponse(BaseModel):
    upload_id: str
    status: str
    error: str | None = None


class ManualCourseRecord(BaseModel):
    code: str
    title: str
    term: str
    year: int
    grade: str
    grade_points: float | None = None
    ects: int = 3


class ManualTranscriptRequest(BaseModel):
    major: str | None = None
    courses: list[ManualCourseRecord]
