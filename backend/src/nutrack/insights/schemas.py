from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ActionSuggestion(BaseModel):
    label: str
    description: str
    action_type: Literal[
        "take_mock",
        "start_flashcards",
        "view_mindmap",
        "take_quiz",
        "take_midterm",
    ]
    action_url: str


class InsightLLMResponse(BaseModel):
    short_summary: str
    long_summary: str
    actions: list[ActionSuggestion]


class InsightsResponse(BaseModel):
    short_summary: str
    long_summary: str
    actions: list[ActionSuggestion]
    generated_at: datetime
    cached: bool
