import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from nutrack.courses.models import CourseOffering


class AssessmentType(str, enum.Enum):
    HOMEWORK = "homework"
    QUIZ = "quiz"
    MIDTERM = "midterm"
    FINAL = "final"
    PROJECT = "project"
    LAB = "lab"
    PRESENTATION = "presentation"
    OTHER = "other"


class Assessment(Base, IDMixin, TimestampMixin):
    __tablename__ = "assessments"
    __table_args__ = (
        Index("ix_assessments_user_course", "user_id", "course_id"),
        Index("ix_assessments_user_deadline", "user_id", "deadline"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
    )
    assessment_type: Mapped[AssessmentType] = mapped_column(
        sa.Enum(AssessmentType, name="assessment_type", values_callable=lambda obj: [e.value for e in obj]),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    deadline: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    weight: Mapped[float | None] = mapped_column(Float, nullable=True)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    is_completed: Mapped[bool] = mapped_column(
        sa.Boolean, default=False, nullable=False
    )

    course_offering: Mapped["CourseOffering"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<Assessment(id={self.id}, user_id={self.user_id}, "
            f"course_id={self.course_id}, title={self.title!r})>"
        )
