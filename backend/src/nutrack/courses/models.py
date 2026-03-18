from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin

if TYPE_CHECKING:
    from nutrack.enrollments.models import Enrollment


class Course(Base, IDMixin):
    __tablename__ = "courses"
    __table_args__ = (
        UniqueConstraint(
            "code",
            "level",
            name="uq_courses_code_level",
        ),
    )

    code: Mapped[str] = mapped_column(String(16))
    level: Mapped[str] = mapped_column(String(16))
    title: Mapped[str] = mapped_column(String(256))
    department: Mapped[str | None] = mapped_column(String(64))
    ects: Mapped[int] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)
    pass_grade: Mapped[str | None] = mapped_column(String, nullable=True)
    school: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    academic_level: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )
    credits_us: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )

    offerings: Mapped[list["CourseOffering"]] = relationship(
        back_populates="course",
    )

    def __repr__(self) -> str:
        return (
            f"<Course(course_id={self.id}, code={self.code}, "
            f"level={self.level})>"
        )


class CourseOffering(Base, IDMixin):
    __tablename__ = "course_offerings"
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "term",
            "year",
            "section",
            name="uq_course_offerings_course_term_year_section",
        ),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    term: Mapped[str] = mapped_column(String(16))
    year: Mapped[int] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(
        String(16),
        nullable=True,
    )
    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )
    days: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    meeting_time: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )
    enrolled: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    capacity: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    faculty: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    room: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
    )

    course: Mapped["Course"] = relationship(
        back_populates="offerings",
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        back_populates="course_offering",
    )

    def __repr__(self) -> str:
        return (
            f"<CourseOffering(id={self.id}, course_id={self.course_id}, "
            f"term={self.term}, year={self.year}, section={self.section})>"
        )
