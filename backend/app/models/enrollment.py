import enum

from sqlalchemy import Enum, ForeignKey, Integer, String, UniqueConstraint, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class EnrollmentStatus(str, enum.Enum):
    PASSED = "passed"
    IN_PROGRESS = "in_progress"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class Enrollment(Base, IDMixin, TimestampMixin):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", "semester", name="uq_enrollment"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False
    )
    semester: Mapped[str] = mapped_column(String(16), nullable=False)
    term: Mapped[int] = mapped_column(Integer, nullable=False)
    grade: Mapped[str | None] = mapped_column(String(4))
    grade_points: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[EnrollmentStatus] = mapped_column(
        Enum(EnrollmentStatus), default=EnrollmentStatus.IN_PROGRESS, nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")

    def __repr__(self) -> str:
        return f"<Enrollment user_id={self.user_id} course={self.course_id} semester={self.semester}>"
