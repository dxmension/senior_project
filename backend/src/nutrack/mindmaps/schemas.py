from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class MindmapNode(BaseModel):
    id: str
    label: str
    description: str = ""
    children: list["MindmapNode"] = Field(default_factory=list)


class MindmapLLMNode(BaseModel):
    id: str = Field(..., min_length=1, max_length=64)
    label: str = Field(..., min_length=1, max_length=80)
    description: str = ""
    parent_id: str | None = None
    child_ids: list[str] = Field(default_factory=list)


class MindmapLLMResponse(BaseModel):
    root_id: str = Field(..., min_length=1, max_length=64)
    nodes: list[MindmapLLMNode] = Field(default_factory=list)


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


class MindmapGenerationQueuedResponse(BaseModel):
    task_id: str
    status: str


class MindmapGenerationStatusResponse(BaseModel):
    task_id: str
    status: str
    mindmap: SavedMindmapResponse | None = None
    error_message: str | None = None


class SavedMindmapResponse(BaseModel):
    id: int
    course_id: int
    week: int
    topic: str
    root: MindmapNode
    created_at: datetime


MindmapNode.model_rebuild()
