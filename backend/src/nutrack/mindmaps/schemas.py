from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MindmapNode(BaseModel):
    id: str
    label: str
    description: str = ""
    children: list[MindmapNode] = []


# Kept for the standalone /generate endpoint (no persistence)
class MindmapRequest(BaseModel):
    topic: str = Field(..., min_length=1, max_length=500)
    depth: int = Field(default=3, ge=1, le=5)


class MindmapResponse(BaseModel):
    topic: str
    root: MindmapNode


# Persisted mindmap request — tied to a course week (topic derived from materials)
class GenerateMindmapRequest(BaseModel):
    week: int = Field(..., ge=1, le=15)
    depth: int = Field(default=3, ge=1, le=5)


class SavedMindmapResponse(BaseModel):
    id: int
    course_id: int
    week: int
    topic: str
    root: MindmapNode
    created_at: datetime
