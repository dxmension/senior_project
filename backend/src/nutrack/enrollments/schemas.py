from pydantic import BaseModel


class EnrollmentItemResponse(BaseModel):
    user_id: int
    course_id: int
    catalog_course_id: int
    course_code: str
    section: str | None = None
    course_title: str
    ects: int
    grade: str | None = None
    grade_points: float | None = None
    term: str
    year: int
    status: str
    meeting_time: str | None = None
    room: str | None = None


class CreateEnrollmentRequest(BaseModel):
    course_id: int
    course_overload_acknowledged: bool = False


class DeleteEnrollmentResponse(BaseModel):
    deleted: bool
