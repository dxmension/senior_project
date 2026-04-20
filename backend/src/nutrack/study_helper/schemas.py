from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class TopicItem(BaseModel):
    name: str
    source: Literal["mindmap", "material"]


class TopicListResponse(BaseModel):
    topics: list[TopicItem]


class WeekSummaryLLMResponse(BaseModel):
    summary: str
    topics: list[str]


class WeekOverviewResponse(BaseModel):
    week: int
    summary: str
    topics: list[TopicItem]
    has_materials: bool


class KeyPoint(BaseModel):
    id: str
    label: str
    short_description: str


class OverviewLLMResponse(BaseModel):
    summary: str
    key_points: list[KeyPoint]


class StudyGuideOverview(BaseModel):
    summary: str
    key_points: list[KeyPoint]


class StudyGuideResponse(BaseModel):
    id: int
    topic: str
    source_type: str
    overview: StudyGuideOverview
    details: dict[str, Any]
    created_at: datetime


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    week: int | None = Field(default=None, ge=1, le=15)


class DetailLLMResponse(BaseModel):
    explanation: str


class DetailResponse(BaseModel):
    point_id: str
    explanation: str


class DeepDiveLLMResponse(BaseModel):
    content: str


class DeepDiveResponse(BaseModel):
    point_id: str
    dive_type: str
    content: str


class TopicExtractionLLMResponse(BaseModel):
    topics: list[str]
