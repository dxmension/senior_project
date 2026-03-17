from datetime import date

from pydantic import BaseModel, Field


class CourseEntity(BaseModel):
    code: str = Field(min_length=1, max_length=16)
    title: str = Field(min_length=1, max_length=256)
    department: str | None = Field(default=None, max_length=64)
    level: str = Field(min_length=1, max_length=16)
    term: str | None = Field(default=None, max_length=16)
    year: int | None = Field(default=None, ge=2000)
    ects: int = Field(ge=0)
    description: str | None = None
    school: str | None = Field(default=None, max_length=32)
    academic_level: str | None = Field(default=None, max_length=16)
    section: str | None = Field(default=None, max_length=16)
    credits_us: float | None = Field(default=None, ge=0)
    start_date: date | None = None
    end_date: date | None = None
    days: str | None = Field(default=None, max_length=64)
    meeting_time: str | None = Field(default=None, max_length=64)
    enrolled: int | None = Field(default=None, ge=0)
    capacity: int | None = Field(default=None, ge=0)
    faculty: str | None = None
    room: str | None = Field(default=None, max_length=128)
