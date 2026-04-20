from sqlalchemy import ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from nutrack.models import Base, IDMixin, TimestampMixin


class Mindmap(Base, IDMixin, TimestampMixin):
    __tablename__ = "mindmaps"
    __table_args__ = (
        Index("ix_mindmaps_user_course", "user_id", "course_id"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    # course_id references course_offerings.id (consistent with rest of app)
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("course_offerings.id", ondelete="CASCADE"), nullable=False
    )
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    tree_json: Mapped[dict] = mapped_column(JSON, nullable=False)
