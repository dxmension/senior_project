from pydantic import BaseModel, Field


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
