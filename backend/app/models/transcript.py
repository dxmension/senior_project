import enum

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class TranscriptStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transcript(Base, IDMixin, TimestampMixin):
    __tablename__ = "transcripts"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    file_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[TranscriptStatus] = mapped_column(
        Enum(TranscriptStatus), default=TranscriptStatus.PENDING, nullable=False
    )
    raw_text: Mapped[str | None] = mapped_column(Text)

    major: Mapped[str | None] = mapped_column(String(128))
    gpa: Mapped[float | None] = mapped_column(Float)
    total_credits_earned: Mapped[int | None] = mapped_column(Integer)
    total_credits_enrolled: Mapped[int | None] = mapped_column(Integer)
    parsed_data: Mapped[dict | None] = mapped_column(JSONB)
    error_message: Mapped[str | None] = mapped_column(Text)

    user: Mapped["User"] = relationship(back_populates="transcript")

    def __repr__(self) -> str:
        return f"<Transcript user_id={self.user_id} status={self.status}>"
