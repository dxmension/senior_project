from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.flashcards.exceptions import (
    FlashcardDeckNotFoundError,
    FlashcardSessionAlreadyCompletedError,
    FlashcardSessionNotFoundError,
)
from nutrack.flashcards.generation import FlashcardGenerationOptions, FlashcardGenerationService
from nutrack.flashcards.models import FlashcardDifficulty, FlashcardSessionStatus
from nutrack.flashcards.repository import (
    FlashcardDeckRepository,
    FlashcardSessionCardRepository,
    FlashcardSessionRepository,
)
from nutrack.flashcards.schemas import (
    FlashcardCardStats,
    FlashcardDeckHistoryResponse,
    FlashcardDeckListItem,
    FlashcardDeckResponse,
    FlashcardItemResponse,
    FlashcardSessionHistoryItem,
    FlashcardSessionResponse,
    FlashcardSessionReviewResponse,
)
from nutrack.storage import ObjectStorage


def _status_value(value: FlashcardSessionStatus | str) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _grade_letter(pct: float) -> str:
    if pct >= 90:
        return "A"
    if pct >= 80:
        return "B"
    if pct >= 70:
        return "C"
    if pct >= 60:
        return "D"
    return "F"


def _card_response(card) -> FlashcardItemResponse:
    return FlashcardItemResponse(
        id=card.id,
        position=card.position,
        question=card.question,
        answer=card.answer,
        topic=card.topic,
    )


def _session_grade_pct(session_obj) -> float | None:
    cards = session_obj.session_cards
    if not cards:
        return None
    # Easy = full credit, medium = half credit, hard = no credit
    score = sum(c.times_easy + c.times_medium * 0.5 for c in cards)
    total = sum(c.times_easy + c.times_medium + c.times_hard for c in cards)
    if total == 0:
        return None
    return round(score / total * 100, 1)


def _deck_list_item(deck) -> FlashcardDeckListItem:
    completed = [
        s for s in deck.sessions
        if _status_value(s.status) == FlashcardSessionStatus.COMPLETED.value
    ]
    completed_sorted = sorted(completed, key=lambda s: s.completed_at or s.started_at)
    grade_pcts = [g for s in completed_sorted if (g := _session_grade_pct(s)) is not None]

    latest_pct = grade_pcts[-1] if grade_pcts else None
    best_pct = max(grade_pcts) if grade_pcts else None
    avg_pct = round(sum(grade_pcts) / len(grade_pcts), 1) if grade_pcts else None
    latest_session_id = completed_sorted[-1].id if completed_sorted else None

    return FlashcardDeckListItem(
        id=deck.id,
        course_id=deck.course_id,
        title=deck.title,
        card_count=deck.card_count,
        difficulty=deck.difficulty,
        created_at=deck.created_at,
        completed_sessions=len(completed),
        latest_grade_pct=latest_pct,
        latest_grade_letter=_grade_letter(latest_pct) if latest_pct is not None else None,
        average_grade_pct=avg_pct,
        best_grade_pct=best_pct,
        latest_completed_session_id=latest_session_id,
    )


def _deck_response(deck) -> FlashcardDeckResponse:
    return FlashcardDeckResponse(
        id=deck.id,
        course_id=deck.course_id,
        title=deck.title,
        card_count=deck.card_count,
        difficulty=deck.difficulty,
        created_at=deck.created_at,
        cards=[_card_response(c) for c in sorted(deck.cards, key=lambda c: c.position)],
    )


def _session_response(session_obj) -> FlashcardSessionResponse:
    cards = sorted(session_obj.deck.cards, key=lambda c: c.position)
    card_stats: dict[int, FlashcardCardStats] = {}
    for sc in session_obj.session_cards:
        card_stats[sc.flashcard_id] = FlashcardCardStats(
            times_seen=sc.times_seen,
            times_easy=sc.times_easy,
            times_medium=sc.times_medium,
            times_hard=sc.times_hard,
            last_response=sc.last_response,
        )
    return FlashcardSessionResponse(
        id=session_obj.id,
        deck_id=session_obj.deck_id,
        deck_title=session_obj.deck.title,
        status=_status_value(session_obj.status),
        started_at=session_obj.started_at,
        cards=[_card_response(c) for c in cards],
        card_stats=card_stats,
    )


def _review_response(session_obj) -> FlashcardSessionReviewResponse:
    total_easy = sum(c.times_easy for c in session_obj.session_cards)
    total_medium = sum(c.times_medium for c in session_obj.session_cards)
    total_hard = sum(c.times_hard for c in session_obj.session_cards)
    total_responses = total_easy + total_medium + total_hard
    # Easy = full credit, medium = half credit, hard = no credit
    score = total_easy + total_medium * 0.5
    grade_pct = round((score / total_responses * 100) if total_responses > 0 else 0, 1)

    struggled = sorted(
        [sc for sc in session_obj.session_cards if sc.times_hard + sc.times_medium > 0],
        key=lambda c: c.times_hard * 2 + c.times_medium,
        reverse=True,
    )[:5]
    top_cards = [_card_response(sc.flashcard) for sc in struggled]

    ai_data: dict = {}
    if session_obj.ai_review:
        try:
            ai_data = json.loads(session_obj.ai_review)
        except Exception:
            pass

    return FlashcardSessionReviewResponse(
        session_id=session_obj.id,
        deck_id=session_obj.deck_id,
        deck_title=session_obj.deck.title,
        total_cards=len(session_obj.deck.cards),
        total_responses=total_responses,
        easy_count=total_easy,
        medium_count=total_medium,
        hard_count=total_hard,
        grade_pct=grade_pct,
        grade_letter=_grade_letter(grade_pct),
        top_struggled_cards=top_cards,
        ai_summary=ai_data.get("summary", ""),
        ai_weak_topics=ai_data.get("weak_topics", []),
        ai_study_plan=ai_data.get("study_plan", ""),
    )


class FlashcardsService:
    def __init__(
        self,
        session: AsyncSession,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.session = session
        self.generation = FlashcardGenerationService(session, storage)
        self.deck_repo = FlashcardDeckRepository(session)
        self.session_repo = FlashcardSessionRepository(session)
        self.session_card_repo = FlashcardSessionCardRepository(session)

    async def generate_deck(
        self,
        user_id: int,
        course_id: int,
        course_label: str,
        *,
        difficulty: str = "medium",
        card_count: int = 20,
        title: str | None = None,
        selected_upload_ids: list[int] | None = None,
        selected_shared_material_ids: list[int] | None = None,
    ) -> FlashcardDeckResponse:
        opts = FlashcardGenerationOptions(
            difficulty=FlashcardDifficulty(difficulty),
            card_count=card_count,
            title=title,
            selected_upload_ids=selected_upload_ids,
            selected_shared_material_ids=selected_shared_material_ids,
        )
        deck = await self.generation.generate_deck(course_id, user_id, course_label, opts)
        return _deck_response(deck)

    async def list_decks(
        self,
        user_id: int,
        *,
        course_id: int | None = None,
    ) -> list[FlashcardDeckListItem]:
        if course_id is not None:
            decks = await self.deck_repo.list_by_user_and_course(user_id, course_id)
        else:
            decks = await self.deck_repo.list_by_user(user_id)
        return [_deck_list_item(d) for d in decks]

    async def get_deck(self, user_id: int, deck_id: int) -> FlashcardDeckResponse:
        deck = await self.deck_repo.get_by_id(deck_id)
        if deck is None or deck.owner_user_id != user_id:
            raise FlashcardDeckNotFoundError()
        return _deck_response(deck)

    async def delete_deck(self, user_id: int, deck_id: int) -> None:
        deck = await self.deck_repo.get_by_id(deck_id)
        if deck is None or deck.owner_user_id != user_id:
            raise FlashcardDeckNotFoundError()
        await self.deck_repo.delete(deck_id)
        await self.session.commit()

    async def start_session(self, user_id: int, deck_id: int) -> FlashcardSessionResponse:
        deck = await self.deck_repo.get_by_id(deck_id)
        if deck is None or deck.owner_user_id != user_id:
            raise FlashcardDeckNotFoundError()

        now = datetime.now(timezone.utc)
        session_obj = await self.session_repo.create(
            deck_id=deck_id,
            user_id=user_id,
            status=FlashcardSessionStatus.IN_PROGRESS.value,
            started_at=now,
        )
        await self.session.commit()
        session_obj = await self.session_repo.get_by_id(session_obj.id)
        return _session_response(session_obj)  # type: ignore[arg-type]

    async def get_session(self, user_id: int, session_id: int) -> FlashcardSessionResponse:
        session_obj = await self.session_repo.get_by_id(session_id)
        if session_obj is None or session_obj.user_id != user_id:
            raise FlashcardSessionNotFoundError()
        return _session_response(session_obj)

    async def record_response(
        self,
        user_id: int,
        session_id: int,
        flashcard_id: int,
        response: str,
    ) -> None:
        session_obj = await self.session_repo.get_by_id(session_id)
        if session_obj is None or session_obj.user_id != user_id:
            raise FlashcardSessionNotFoundError()
        if _status_value(session_obj.status) == FlashcardSessionStatus.COMPLETED.value:
            raise FlashcardSessionAlreadyCompletedError()
        await self.session_card_repo.upsert_response(session_id, flashcard_id, response)
        await self.session.commit()

    async def complete_session(
        self,
        user_id: int,
        session_id: int,
    ) -> FlashcardSessionReviewResponse:
        session_obj = await self.session_repo.get_by_id(session_id)
        if session_obj is None or session_obj.user_id != user_id:
            raise FlashcardSessionNotFoundError()

        if (
            _status_value(session_obj.status) == FlashcardSessionStatus.COMPLETED.value
            and session_obj.ai_review
        ):
            return _review_response(session_obj)

        total_easy = sum(c.times_easy for c in session_obj.session_cards)
        total_medium = sum(c.times_medium for c in session_obj.session_cards)
        total_hard = sum(c.times_hard for c in session_obj.session_cards)
        total_responses = total_easy + total_medium + total_hard

        struggled = sorted(
            [sc for sc in session_obj.session_cards if sc.times_hard + sc.times_medium > 0],
            key=lambda c: c.times_hard * 2 + c.times_medium,
            reverse=True,
        )[:5]

        stats = {
            "total_cards": len(session_obj.deck.cards),
            "easy_count": total_easy,
            "medium_count": total_medium,
            "hard_count": total_hard,
            "total_responses": total_responses,
            "struggled_cards": [
                {"question": sc.flashcard.question, "topic": sc.flashcard.topic}
                for sc in struggled
            ],
        }

        ai_result = await self.generation.generate_ai_review(stats)

        ai_review_json = json.dumps({
            "summary": ai_result.summary,
            "weak_topics": ai_result.weak_topics,
            "study_plan": ai_result.study_plan,
        })

        now = datetime.now(timezone.utc)
        await self.session_repo.update(
            session_obj,
            status=FlashcardSessionStatus.COMPLETED.value,
            completed_at=now,
            ai_review=ai_review_json,
        )
        await self.session.commit()

        session_obj = await self.session_repo.get_by_id(session_id)
        return _review_response(session_obj)  # type: ignore[arg-type]

    async def get_review(
        self, user_id: int, session_id: int
    ) -> FlashcardSessionReviewResponse:
        session_obj = await self.session_repo.get_by_id(session_id)
        if session_obj is None or session_obj.user_id != user_id:
            raise FlashcardSessionNotFoundError()
        if _status_value(session_obj.status) != FlashcardSessionStatus.COMPLETED.value:
            raise FlashcardSessionNotFoundError()
        return _review_response(session_obj)

    async def get_deck_history(
        self, user_id: int, deck_id: int
    ) -> FlashcardDeckHistoryResponse:
        deck = await self.deck_repo.get_by_id_with_sessions(deck_id)
        if deck is None or deck.owner_user_id != user_id:
            raise FlashcardDeckNotFoundError()

        completed = sorted(
            [
                s for s in deck.sessions
                if _status_value(s.status) == FlashcardSessionStatus.COMPLETED.value
                and s.completed_at is not None
            ],
            key=lambda s: s.completed_at,
        )

        history_items: list[FlashcardSessionHistoryItem] = []
        grade_pcts: list[float] = []
        for s in completed:
            easy = sum(c.times_easy for c in s.session_cards)
            medium = sum(c.times_medium for c in s.session_cards)
            hard = sum(c.times_hard for c in s.session_cards)
            total = easy + medium + hard
            # Easy = full credit, medium = half credit, hard = no credit
            score = easy + medium * 0.5
            pct = round(score / total * 100, 1) if total > 0 else 0.0
            grade_pcts.append(pct)
            history_items.append(FlashcardSessionHistoryItem(
                session_id=s.id,
                completed_at=s.completed_at,
                grade_pct=pct,
                grade_letter=_grade_letter(pct),
                easy_count=easy,
                medium_count=medium,
                hard_count=hard,
                total_responses=total,
            ))

        avg_pct = round(sum(grade_pcts) / len(grade_pcts), 1) if grade_pcts else None
        best_pct = max(grade_pcts) if grade_pcts else None

        # Weighted predicted grade: last 3 sessions (most recent weighted highest)
        # Weights are normalised so they always sum to 1.0 regardless of session count
        predicted_pct: float | None = None
        if grade_pcts:
            recent = grade_pcts[-3:]
            raw_weights = [0.2, 0.3, 0.5][3 - len(recent):]
            total_w = sum(raw_weights)
            weights = [w / total_w for w in raw_weights]
            predicted_pct = round(sum(p * w for p, w in zip(recent, weights)), 1)

        return FlashcardDeckHistoryResponse(
            deck_id=deck.id,
            deck_title=deck.title,
            total_completed=len(completed),
            average_grade_pct=avg_pct,
            best_grade_pct=best_pct,
            predicted_grade_pct=predicted_pct,
            predicted_grade_letter=_grade_letter(predicted_pct) if predicted_pct is not None else None,
            sessions=history_items,
        )
