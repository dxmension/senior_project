from pydantic import BaseModel, Field


class InvalidScheduleRow(BaseModel):
    row: int
    course_code: str | None = None
    course_name: str | None = None
    error: str


class CourseScheduleUploadResponse(BaseModel):
    processed_rows: int
    inserted_count: int
    updated_count: int
    invalid_rows_count: int = 0
    invalid_rows: list[InvalidScheduleRow] = Field(default_factory=list)
