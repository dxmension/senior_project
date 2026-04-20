from __future__ import annotations

import logging
from dataclasses import dataclass

from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.course_materials.models import CourseMaterialUpload, MaterialUploadStatus
from nutrack.course_materials.repository import (
    CourseMaterialLibraryRepository,
    CourseMaterialUploadRepository,
)
from nutrack.flashcards.models import FlashcardDeck, FlashcardDifficulty
from nutrack.flashcards.repository import FlashcardDeckRepository, FlashcardRepository
from nutrack.mock_exams.generation import (
    _dedupe_uploads,
    _join_parts,
    _material_parts,
    _ordered_uploads,
)
from nutrack.storage import ObjectStorage
from nutrack.tools.llm.service import parse_structured_response

logger = logging.getLogger(__name__)
DEFAULT_MODEL = "gpt-5-mini"


@dataclass
class FlashcardGenerationOptions:
    difficulty: FlashcardDifficulty = FlashcardDifficulty.MEDIUM
    card_count: int = 20
    title: str | None = None
    selected_upload_ids: list[int] | None = None
    selected_shared_material_ids: list[int] | None = None


class GeneratedFlashcard(BaseModel):
    question: str = Field(min_length=1)
    answer: str = Field(min_length=1)
    topic: str | None = None


class FlashcardDeckOutput(BaseModel):
    title: str = Field(min_length=1)
    flashcards: list[GeneratedFlashcard] = Field(min_length=1, max_length=60)


class AIReviewOutput(BaseModel):
    summary: str
    weak_topics: list[str]
    study_plan: str


_DIFFICULTY_PROMPTS: dict[FlashcardDifficulty, str] = {
    FlashcardDifficulty.EASY: "Create straightforward recall questions covering basic concepts.",
    FlashcardDifficulty.MEDIUM: "Create questions that test understanding and application of concepts.",
    FlashcardDifficulty.HARD: "Create challenging questions requiring deep analysis and critical thinking.",
}

_SYSTEM_PROMPT = """\
You are generating university study flashcards from course materials.
Create clear question/answer pairs that help students master the material.
Each card should focus on one concept. The answer should be concise but complete.
Return a JSON object with:
- title: a short descriptive title for this deck
- flashcards: array of {question, answer, topic} objects
The topic field groups related cards (e.g. "Data Structures", "Sorting Algorithms").
Cover the material broadly and avoid duplicates.
"""

_REVIEW_SYSTEM_PROMPT = """\
You are analyzing a student's flashcard study session.
Provide a concise, actionable study review based on their performance.
Return JSON with:
- summary: 2-3 sentence overall assessment of the student's performance
- weak_topics: list of topic names the student struggled with most
- study_plan: a string with 3-5 bullet points (use "• " prefix) of specific actions to improve
"""


class FlashcardGenerationService:
    def __init__(
        self,
        session: AsyncSession,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.session = session
        self.storage = storage or ObjectStorage()
        self.deck_repo = FlashcardDeckRepository(session)
        self.card_repo = FlashcardRepository(session)
        self.upload_repo = CourseMaterialUploadRepository(session)
        self.library_repo = CourseMaterialLibraryRepository(session)

    async def generate_deck(
        self,
        course_id: int,
        user_id: int,
        course_label: str,
        opts: FlashcardGenerationOptions,
    ) -> FlashcardDeck:
        uploads = await self._eligible_uploads(
            user_id, course_id, selected_ids=opts.selected_upload_ids
        )
        shared = await self._shared_uploads(opts.selected_shared_material_ids)
        all_uploads = _dedupe_uploads(uploads + shared)
        parts = await _material_parts(self.storage, all_uploads)
        material_text = _join_parts(parts, 24000)

        user_prompt = _build_generation_prompt(course_label, material_text, opts)
        result = await parse_structured_response(
            system_prompt=_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=FlashcardDeckOutput,
            model=DEFAULT_MODEL,
            temperature=0.4,
        )

        title = opts.title or result.title
        deck = await self.deck_repo.create(
            course_id=course_id,
            title=title,
            card_count=len(result.flashcards),
            difficulty=opts.difficulty.value,
            owner_user_id=user_id,
        )

        card_payloads = [
            {
                "deck_id": deck.id,
                "position": i + 1,
                "question": card.question.strip(),
                "answer": card.answer.strip(),
                "topic": card.topic,
            }
            for i, card in enumerate(result.flashcards)
        ]
        await self.card_repo.bulk_create(card_payloads)
        await self.session.commit()

        refreshed = await self.deck_repo.get_by_id(deck.id)
        return refreshed  # type: ignore[return-value]

    async def generate_ai_review(self, session_stats: dict) -> AIReviewOutput:
        user_prompt = _build_review_prompt(session_stats)
        return await parse_structured_response(
            system_prompt=_REVIEW_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            response_model=AIReviewOutput,
            model=DEFAULT_MODEL,
            temperature=0.5,
        )

    async def _eligible_uploads(
        self,
        user_id: int,
        course_offering_id: int,
        *,
        selected_ids: list[int] | None = None,
    ) -> list[CourseMaterialUpload]:
        uploads = await self.upload_repo.list_user_uploads(user_id, course_offering_id)
        personal = [
            item for item in uploads if item.upload_status == MaterialUploadStatus.COMPLETED
        ]
        if selected_ids is not None:
            id_set = set(selected_ids)
            personal = [item for item in personal if item.id in id_set]
        return _ordered_uploads(_dedupe_uploads(personal))

    async def _shared_uploads(
        self, selected_shared_ids: list[int] | None
    ) -> list[CourseMaterialUpload]:
        if not selected_shared_ids:
            return []
        entries = await self.library_repo.list_by_ids(selected_shared_ids)
        return [
            entry.upload
            for entry in entries
            if entry.upload.upload_status == MaterialUploadStatus.COMPLETED
        ]


def _build_generation_prompt(
    course_label: str,
    material_text: str,
    opts: FlashcardGenerationOptions,
) -> str:
    difficulty_note = _DIFFICULTY_PROMPTS[opts.difficulty]
    return (
        f"Course: {course_label}\n"
        f"Target card count: {opts.card_count}\n"
        f"Difficulty instruction: {difficulty_note}\n\n"
        "Study materials:\n"
        f"{material_text}"
    )


def _build_review_prompt(stats: dict) -> str:
    lines = [
        f"Total unique cards in deck: {stats['total_cards']}",
        f"Easy responses: {stats['easy_count']}",
        f"Medium responses: {stats['medium_count']}",
        f"Hard responses: {stats['hard_count']}",
        f"Total responses recorded: {stats['total_responses']}",
        "",
        "Cards the student struggled with most (medium + hard responses):",
    ]
    for card in stats.get("struggled_cards", []):
        topic = card.get("topic") or "General"
        lines.append(f"- [{topic}] {card['question']}")
    return "\n".join(lines)
