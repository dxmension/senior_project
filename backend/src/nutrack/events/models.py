import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from nutrack.categories.models import Category


class RecurrenceType(str, enum.Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"
    BIWEEKLY = "biweekly"
    MONTHLY = "monthly"


class Event(Base, IDMixin, TimestampMixin):
    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_user_start_at", "user_id", "start_at"),
        Index("ix_events_user_category", "user_id", "category_id"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    category_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_all_day: Mapped[bool] = mapped_column(sa.Boolean, default=False, nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    recurrence: Mapped[RecurrenceType] = mapped_column(
        sa.Enum(RecurrenceType, name="recurrence_type", values_callable=lambda obj: [e.value for e in obj]),
        default=RecurrenceType.NONE,
        nullable=False,
    )
    recurrence_end_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    category: Mapped["Category | None"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<Event(id={self.id}, user_id={self.user_id}, title={self.title!r}, "
            f"start_at={self.start_at})>"
        )
