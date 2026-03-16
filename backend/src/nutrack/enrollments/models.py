import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, TimestampMixin

if TYPE_CHECKING:
    from nutrack.courses.models import Course
    from nutrack.users.models import User


class EnrollmentStatus(str, enum.Enum):
    PASSED = "passed"
    IN_PROGRESS = "in_progress"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"
    AUDIT = "audit"
    INCOMPLETE = "incomplete"


class Enrollment(Base, TimestampMixin):
    __tablename__ = "enrollments"

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        primary_key=True,
    )
    semester: Mapped[str] = mapped_column(String(16), primary_key=True)
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
