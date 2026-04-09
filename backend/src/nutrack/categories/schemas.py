import re
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

HEX_COLOR_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")


def _validate_hex_color(v: str) -> str:
    if not HEX_COLOR_RE.match(v):
        raise ValueError("color must be a valid hex color, e.g. '#FF5733'")
    return v


class CreateCategoryRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    color: str

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, v: str) -> str:
        return _validate_hex_color(v)


class UpdateCategoryRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    color: str | None = None

    @field_validator("color")
    @classmethod
    def color_must_be_hex(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return _validate_hex_color(v)


class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime
    updated_at: datetime
