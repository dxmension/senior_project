import enum

from sqlalchemy import Enum, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from nutrack.models import Base, IDMixin, TimestampMixin


class StudyGuideSourceType(str, enum.Enum):
    MATERIALS = "materials"
    AI_KNOWLEDGE = "ai_knowledge"
    HYBRID = "hybrid"


class StudyGuide(Base, IDMixin, TimestampMixin):
    __tablename__ = "study_guides"
    __table_args__ = (
        Index("ix_study_guides_user_course_topic", "user_id", "course_id", "topic"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
    )
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    overview_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    details_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    source_type: Mapped[StudyGuideSourceType] = mapped_column(
        Enum(
            StudyGuideSourceType,
            values_callable=lambda e: [m.value for m in e],
        ),
        nullable=False,
    )
    materials_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )


class WeekOverviewCache(Base, IDMixin, TimestampMixin):
    __tablename__ = "week_overview_cache"
    __table_args__ = (
        Index(
            "ix_week_overview_cache_user_course_week",
            "user_id",
            "course_id",
            "week",
            unique=True,
        ),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str] = mapped_column(String(2000), nullable=False)
    topics_json: Mapped[list] = mapped_column(JSON, nullable=False)
    materials_hash: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
