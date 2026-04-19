from datetime import datetime

from pydantic import BaseModel


class HandbookUploadResponse(BaseModel):
    id: int
    enrollment_year: int
    filename: str
    status: str
    error: str | None = None
    created_at: datetime


class HandbookStatusResponse(BaseModel):
    id: int
    enrollment_year: int
    filename: str
    status: str
    majors_parsed: list[str]
    error: str | None
    created_at: datetime
    updated_at: datetime
