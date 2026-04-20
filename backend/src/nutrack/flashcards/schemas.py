from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class GenerateFlashcardDeckRequest(BaseModel):
    course_id: int
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    card_count: int = Field(default=20, ge=5, le=60)
    title: str | None = None
    selected_upload_ids: list[int] | None = None
    selected_shared_material_ids: list[int] | None = None


class FlashcardItemResponse(BaseModel):
    id: int
    position: int
    question: str
    answer: str
    topic: str | None


class FlashcardDeckListItem(BaseModel):
    id: int
    course_id: int
    title: str
    card_count: int
    difficulty: str
    created_at: datetime
    completed_sessions: int
    latest_grade_pct: float | None
    latest_grade_letter: str | None
    average_grade_pct: float | None
    best_grade_pct: float | None
    latest_completed_session_id: int | None


class FlashcardDeckResponse(BaseModel):
    id: int
    course_id: int
    title: str
    card_count: int
    difficulty: str
    created_at: datetime
    cards: list[FlashcardItemResponse]


class CardResponseRequest(BaseModel):
    response: Literal["easy", "medium", "hard"]


class FlashcardCardStats(BaseModel):
    times_seen: int
    times_easy: int
    times_medium: int
    times_hard: int
    last_response: str | None


class FlashcardSessionResponse(BaseModel):
    id: int
    deck_id: int
    deck_title: str
    status: str
    started_at: datetime
    cards: list[FlashcardItemResponse]
    card_stats: dict[int, FlashcardCardStats]


class FlashcardSessionHistoryItem(BaseModel):
    session_id: int
    completed_at: datetime
    grade_pct: float
    grade_letter: str
    easy_count: int
    medium_count: int
    hard_count: int
    total_responses: int


class FlashcardDeckHistoryResponse(BaseModel):
    deck_id: int
    deck_title: str
    total_completed: int
    average_grade_pct: float | None
    best_grade_pct: float | None
    predicted_grade_pct: float | None
    predicted_grade_letter: str | None
    sessions: list[FlashcardSessionHistoryItem]


class FlashcardSessionReviewResponse(BaseModel):
    session_id: int
    deck_id: int
    deck_title: str
    total_cards: int
    total_responses: int
    easy_count: int
    medium_count: int
    hard_count: int
    grade_pct: float
    grade_letter: str
    top_struggled_cards: list[FlashcardItemResponse]
    ai_summary: str
    ai_weak_topics: list[str]
    ai_study_plan: str
