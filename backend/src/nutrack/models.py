import enum
from datetime import datetime

from sqlalchemy import (
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint, DateTime, func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

1
class IDMixin:
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
        unique=True,
    )



class EnrollmentStatus(str, enum.Enum):
    PASSED = "passed"
    IN_PROGRESS = "in_progress"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"
    AUDIT = "audit"
    INCOMPLETE = "incomplete"


class Enrollment(Base, IDMixin, TimestampMixin):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "course_id",
            "semester",
            name="uq_enrollment",
        ),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    semester: Mapped[str] = mapped_column(String(16), nullable=False)
    grade: Mapped[str | None] = mapped_column(String(4))
    grade_points: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus),
        default=EnrollmentStatus.IN_PROGRESS,
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        return (
            f"<Enrollment user_id={self.user_id} course={self.course_id} "
            f"semester={self.semester}>"
        )