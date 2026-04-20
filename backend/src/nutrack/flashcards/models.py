import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from nutrack.courses.models import CourseOffering
    from nutrack.users.models import User


class FlashcardDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class FlashcardSessionStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class FlashcardDeck(Base, IDMixin, TimestampMixin):
    __tablename__ = "flashcard_decks"
    __table_args__ = (
        Index("ix_flashcard_decks_course_id", "course_id"),
        Index("ix_flashcard_decks_owner_user_id", "owner_user_id"),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    card_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False, default="medium")
    owner_user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    course: Mapped["CourseOffering"] = relationship()
    owner_user: Mapped["User"] = relationship()
    cards: Mapped[list["Flashcard"]] = relationship(
        back_populates="deck",
        cascade="all, delete-orphan",
        order_by="Flashcard.position",
    )
    sessions: Mapped[list["FlashcardSession"]] = relationship(
        back_populates="deck",
        cascade="all, delete-orphan",
    )


class Flashcard(Base, IDMixin, TimestampMixin):
    __tablename__ = "flashcards"
    __table_args__ = (
        UniqueConstraint("deck_id", "position", name="uq_flashcards_deck_position"),
        Index("ix_flashcards_deck_id", "deck_id"),
    )

    deck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("flashcard_decks.id", ondelete="CASCADE"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    topic: Mapped[str | None] = mapped_column(String(128), nullable=True)

    deck: Mapped[FlashcardDeck] = relationship(back_populates="cards")
    session_cards: Mapped[list["FlashcardSessionCard"]] = relationship(
        back_populates="flashcard",
        cascade="all, delete-orphan",
    )


class FlashcardSession(Base, IDMixin, TimestampMixin):
    __tablename__ = "flashcard_sessions"
    __table_args__ = (
        Index("ix_flashcard_sessions_deck_id", "deck_id"),
        Index("ix_flashcard_sessions_user_id", "user_id"),
    )

    deck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("flashcard_decks.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=FlashcardSessionStatus.IN_PROGRESS.value,
    )
    started_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    ai_review: Mapped[str | None] = mapped_column(Text, nullable=True)

    deck: Mapped[FlashcardDeck] = relationship(back_populates="sessions")
    user: Mapped["User"] = relationship()
    session_cards: Mapped[list["FlashcardSessionCard"]] = relationship(
        back_populates="session",
        cascade="all, delete-orphan",
    )


class FlashcardSessionCard(Base, IDMixin, TimestampMixin):
    __tablename__ = "flashcard_session_cards"
    __table_args__ = (
        UniqueConstraint("session_id", "flashcard_id", name="uq_flashcard_session_cards"),
        Index("ix_flashcard_session_cards_session_id", "session_id"),
    )

    session_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("flashcard_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    flashcard_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("flashcards.id", ondelete="CASCADE"),
        nullable=False,
    )
    times_seen: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    times_easy: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    times_medium: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    times_hard: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_response: Mapped[str | None] = mapped_column(String(16), nullable=True)

    session: Mapped[FlashcardSession] = relationship(back_populates="session_cards")
    flashcard: Mapped[Flashcard] = relationship(back_populates="session_cards")
