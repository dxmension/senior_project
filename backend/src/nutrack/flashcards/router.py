from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.auth.dependencies import get_current_user
from nutrack.courses.models import CourseOffering
from nutrack.database import get_async_session
from nutrack.enrollments.models import Enrollment
from nutrack.flashcards.dependencies import get_flashcards_service
from nutrack.flashcards.schemas import (
    CardResponseRequest,
    FlashcardDeckHistoryResponse,
    FlashcardDeckListItem,
    FlashcardDeckResponse,
    FlashcardSessionResponse,
    FlashcardSessionReviewResponse,
    GenerateFlashcardDeckRequest,
)
from nutrack.flashcards.service import FlashcardsService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


async def _course_label(
    user_id: int,
    course_id: int,
    session: AsyncSession,
) -> str:
    result = await session.execute(
        select(CourseOffering)
        .join(Enrollment, Enrollment.course_id == CourseOffering.id)
        .options(joinedload(CourseOffering.course))
        .where(
            Enrollment.user_id == user_id,
            CourseOffering.id == course_id,
        )
        .limit(1)
    )
    offering = result.scalars().first()
    if offering is None:
        return f"Course {course_id}"
    course = offering.course
    level = (course.level or "").strip()
    code = f"{course.code} {level}" if level and level != "0" else course.code
    return f"{code} - {course.title}"


@router.post(
    "/generate",
    response_model=ApiResponse[FlashcardDeckResponse],
)
async def generate_flashcard_deck(
    body: GenerateFlashcardDeckRequest,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
    session: AsyncSession = Depends(get_async_session),
):
    label = await _course_label(user.id, body.course_id, session)
    deck = await service.generate_deck(
        user.id,
        body.course_id,
        label,
        difficulty=body.difficulty,
        card_count=body.card_count,
        title=body.title,
        selected_upload_ids=body.selected_upload_ids,
        selected_shared_material_ids=body.selected_shared_material_ids,
    )
    return ApiResponse(data=deck)


@router.get(
    "/decks",
    response_model=ApiResponse[list[FlashcardDeckListItem]],
)
async def list_decks(
    course_id: int | None = None,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    decks = await service.list_decks(user.id, course_id=course_id)
    return ApiResponse(data=decks)


@router.get(
    "/decks/{deck_id}",
    response_model=ApiResponse[FlashcardDeckResponse],
)
async def get_deck(
    deck_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    deck = await service.get_deck(user.id, deck_id)
    return ApiResponse(data=deck)


@router.get(
    "/decks/{deck_id}/history",
    response_model=ApiResponse[FlashcardDeckHistoryResponse],
)
async def get_deck_history(
    deck_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    history = await service.get_deck_history(user.id, deck_id)
    return ApiResponse(data=history)


@router.delete("/decks/{deck_id}", response_model=ApiResponse[None])
async def delete_deck(
    deck_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    await service.delete_deck(user.id, deck_id)
    return ApiResponse(data=None)


@router.post(
    "/decks/{deck_id}/sessions",
    response_model=ApiResponse[FlashcardSessionResponse],
)
async def start_session(
    deck_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    session_data = await service.start_session(user.id, deck_id)
    return ApiResponse(data=session_data)


@router.get(
    "/sessions/{session_id}",
    response_model=ApiResponse[FlashcardSessionResponse],
)
async def get_session(
    session_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    session_data = await service.get_session(user.id, session_id)
    return ApiResponse(data=session_data)


@router.post(
    "/sessions/{session_id}/cards/{flashcard_id}/respond",
    response_model=ApiResponse[None],
)
async def record_card_response(
    session_id: int,
    flashcard_id: int,
    body: CardResponseRequest,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    await service.record_response(user.id, session_id, flashcard_id, body.response)
    return ApiResponse(data=None)


@router.post(
    "/sessions/{session_id}/complete",
    response_model=ApiResponse[FlashcardSessionReviewResponse],
)
async def complete_session(
    session_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    review = await service.complete_session(user.id, session_id)
    return ApiResponse(data=review)


@router.get(
    "/sessions/{session_id}/review",
    response_model=ApiResponse[FlashcardSessionReviewResponse],
)
async def get_session_review(
    session_id: int,
    user: User = Depends(get_current_user),
    service: FlashcardsService = Depends(get_flashcards_service),
):
    review = await service.get_review(user.id, session_id)
    return ApiResponse(data=review)
