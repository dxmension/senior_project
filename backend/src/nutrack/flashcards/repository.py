from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nutrack.flashcards.models import (
    Flashcard,
    FlashcardDeck,
    FlashcardSession,
    FlashcardSessionCard,
)


class FlashcardDeckRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs) -> FlashcardDeck:
        deck = FlashcardDeck(**kwargs)
        self.session.add(deck)
        await self.session.flush()
        return deck

    async def get_by_id(self, deck_id: int) -> FlashcardDeck | None:
        result = await self.session.execute(
            select(FlashcardDeck)
            .options(selectinload(FlashcardDeck.cards))
            .where(FlashcardDeck.id == deck_id)
        )
        return result.scalars().first()

    async def get_by_id_with_sessions(self, deck_id: int) -> FlashcardDeck | None:
        result = await self.session.execute(
            select(FlashcardDeck)
            .options(
                selectinload(FlashcardDeck.sessions).selectinload(
                    FlashcardSession.session_cards
                )
            )
            .where(FlashcardDeck.id == deck_id)
        )
        return result.scalars().first()

    async def list_by_user_and_course(self, user_id: int, course_id: int) -> list[FlashcardDeck]:
        result = await self.session.execute(
            select(FlashcardDeck)
            .options(
                selectinload(FlashcardDeck.sessions).selectinload(
                    FlashcardSession.session_cards
                )
            )
            .where(FlashcardDeck.owner_user_id == user_id)
            .where(FlashcardDeck.course_id == course_id)
            .order_by(FlashcardDeck.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_user(self, user_id: int) -> list[FlashcardDeck]:
        result = await self.session.execute(
            select(FlashcardDeck)
            .options(
                selectinload(FlashcardDeck.sessions).selectinload(
                    FlashcardSession.session_cards
                )
            )
            .where(FlashcardDeck.owner_user_id == user_id)
            .order_by(FlashcardDeck.created_at.desc())
        )
        return list(result.scalars().all())

    async def delete(self, deck_id: int) -> None:
        deck = await self.get_by_id(deck_id)
        if deck is not None:
            await self.session.delete(deck)
            await self.session.flush()


class FlashcardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def bulk_create(self, cards: list[dict]) -> list[Flashcard]:
        objects = [Flashcard(**c) for c in cards]
        self.session.add_all(objects)
        await self.session.flush()
        return objects


class FlashcardSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, **kwargs) -> FlashcardSession:
        session_obj = FlashcardSession(**kwargs)
        self.session.add(session_obj)
        await self.session.flush()
        return session_obj

    async def get_by_id(self, session_id: int) -> FlashcardSession | None:
        result = await self.session.execute(
            select(FlashcardSession)
            .options(
                selectinload(FlashcardSession.deck).selectinload(FlashcardDeck.cards),
                selectinload(FlashcardSession.session_cards).selectinload(
                    FlashcardSessionCard.flashcard
                ),
            )
            .where(FlashcardSession.id == session_id)
        )
        return result.scalars().first()

    async def update(self, session_obj: FlashcardSession, **kwargs) -> FlashcardSession:
        for key, value in kwargs.items():
            setattr(session_obj, key, value)
        await self.session.flush()
        return session_obj


class FlashcardSessionCardRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_session_and_card(
        self, session_id: int, flashcard_id: int
    ) -> FlashcardSessionCard | None:
        result = await self.session.execute(
            select(FlashcardSessionCard)
            .where(FlashcardSessionCard.session_id == session_id)
            .where(FlashcardSessionCard.flashcard_id == flashcard_id)
        )
        return result.scalars().first()

    async def upsert_response(
        self, session_id: int, flashcard_id: int, response: str
    ) -> FlashcardSessionCard:
        existing = await self.get_by_session_and_card(session_id, flashcard_id)
        if existing is None:
            card = FlashcardSessionCard(
                session_id=session_id,
                flashcard_id=flashcard_id,
                times_seen=1,
                times_easy=1 if response == "easy" else 0,
                times_medium=1 if response == "medium" else 0,
                times_hard=1 if response == "hard" else 0,
                last_response=response,
            )
            self.session.add(card)
            await self.session.flush()
            return card

        existing.times_seen += 1
        if response == "easy":
            existing.times_easy += 1
        elif response == "medium":
            existing.times_medium += 1
        elif response == "hard":
            existing.times_hard += 1
        existing.last_response = response
        await self.session.flush()
        return existing
