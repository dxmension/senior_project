import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from nutrack.events.models import RecurrenceType

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _validate_hex_color(value: str) -> str:
    if not HEX_COLOR_RE.match(value):
        raise ValueError("color must be a valid hex color, e.g. '#FF5733'")
    return value


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, value: str) -> str:
        return _validate_hex_color(value)


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = None

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_hex_color(value)


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime
    updated_at: datetime


class CreateEventRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime
    end_at: datetime | None = None
    is_all_day: bool = False
    location: str | None = Field(default=None, max_length=255)
    category_id: int | None = None
    recurrence: RecurrenceType = RecurrenceType.NONE
    recurrence_end_at: datetime | None = None

    @field_validator("start_at", "end_at", "recurrence_end_at")
    @classmethod
    def must_be_timezone_aware(cls, v: datetime | None) -> datetime | None:
        if v is not None and v.tzinfo is None:
            raise ValueError("datetime fields must be timezone-aware")
        return v

    @model_validator(mode="after")
    def validate_end_and_recurrence(self) -> "CreateEventRequest":
        if self.end_at is not None and self.end_at <= self.start_at:
            raise ValueError("end_at must be after start_at")
        if self.recurrence != RecurrenceType.NONE:
            if self.recurrence_end_at is None:
                raise ValueError(
                    "recurrence_end_at is required when recurrence is set"
                )
            if self.recurrence_end_at <= self.start_at:
                raise ValueError("recurrence_end_at must be after start_at")
        return self


class UpdateEventRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    is_all_day: bool | None = None
    location: str | None = Field(default=None, max_length=255)
    category_id: int | None = None
    recurrence: RecurrenceType | None = None
    recurrence_end_at: datetime | None = None


class EventResponse(BaseModel):
    id: int
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime | None
    is_all_day: bool
    location: str | None
    recurrence: RecurrenceType
    recurrence_end_at: datetime | None
    category: CategoryResponse | None
    created_at: datetime
    updated_at: datetime
