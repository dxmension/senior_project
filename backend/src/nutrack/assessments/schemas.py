from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Self

from nutrack.assessments.models import AssessmentType


class CreateAssessmentRequest(BaseModel):
    course_id: int
    assessment_type: AssessmentType
    assessment_number: int = Field(ge=1)
    description: str | None = None
    deadline: datetime
    weight: float | None = Field(default=None, ge=0.0, le=100.0)
    max_score: float | None = Field(default=None, ge=0.0)

    @field_validator("deadline")
    @classmethod
    def deadline_must_be_timezone_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("deadline must be timezone-aware")
        return v


class UpdateAssessmentRequest(BaseModel):
    assessment_type: AssessmentType | None = None
    assessment_number: int | None = Field(default=None, ge=1)
    description: str | None = None
    deadline: datetime | None = None
    weight: float | None = None
    score: float | None = Field(default=None, ge=0.0)
    max_score: float | None = Field(default=None, ge=0.0)
    is_completed: bool | None = None

    @model_validator(mode="after")
    def score_within_max(self) -> Self:
        if self.score is not None and self.max_score is not None:
            if self.score > self.max_score:
                raise ValueError("score cannot exceed max_score")
        return self


class AssessmentResponse(BaseModel):
    id: int
    course_id: int
    course_code: str
    course_title: str
    assessment_type: AssessmentType
    assessment_number: int
    title: str
    description: str | None
    deadline: datetime
    weight: float | None
    score: float | None
    max_score: float | None
    is_completed: bool
    created_at: datetime
    updated_at: datetime
