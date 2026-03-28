from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    Date,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from nutrack.enrollments.models import Enrollment
    from nutrack.users.models import User


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
    prerequisites: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    corequisites: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    antirequisites: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_1: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_2: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_3: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority_4: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Tracks which semester's requirements PDF populated the fields above.
    # Spring is prioritised over Fall for the same year.
    requirements_term: Mapped[str | None] = mapped_column(String(16), nullable=True)
    requirements_year: Mapped[int | None] = mapped_column(Integer, nullable=True)

    offerings: Mapped[list["CourseOffering"]] = relationship(
        back_populates="course",
    )
    gpa_stats: Mapped[list["CourseGpaStats"]] = relationship(
        back_populates="course",
    )
    reviews: Mapped[list["CourseReview"]] = relationship(
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


class CourseGpaStats(Base, IDMixin, TimestampMixin):
    __tablename__ = "course_gpa_stats"
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "term",
            "year",
            "section",
            name="uq_course_gpa_stats_course_term_year_section",
        ),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    term: Mapped[str] = mapped_column(String(16))
    year: Mapped[int] = mapped_column(Integer)
    section: Mapped[str | None] = mapped_column(String(16), nullable=True)
    avg_gpa: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_enrolled: Mapped[int | None] = mapped_column(Integer, nullable=True)
    grade_distribution: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    course: Mapped["Course"] = relationship(back_populates="gpa_stats")

    def __repr__(self) -> str:
        return (
            f"<CourseGpaStats(course_id={self.course_id}, "
            f"term={self.term}, year={self.year}, section={self.section})>"
        )


class CourseReview(Base, IDMixin, TimestampMixin):
    __tablename__ = "course_reviews"
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "user_id",
            name="uq_course_reviews_course_user",
        ),
        CheckConstraint("overall_rating BETWEEN 1 AND 5", name="ck_review_overall_rating"),
        CheckConstraint("difficulty IS NULL OR difficulty BETWEEN 1 AND 5", name="ck_review_difficulty"),
        CheckConstraint("informativeness IS NULL OR informativeness BETWEEN 1 AND 5", name="ck_review_informativeness"),
        CheckConstraint("gpa_boost IS NULL OR gpa_boost BETWEEN 1 AND 5", name="ck_review_gpa_boost"),
        CheckConstraint("workload IS NULL OR workload BETWEEN 1 AND 5", name="ck_review_workload"),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    overall_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[int | None] = mapped_column(Integer, nullable=True)
    informativeness: Mapped[int | None] = mapped_column(Integer, nullable=True)
    gpa_boost: Mapped[int | None] = mapped_column(Integer, nullable=True)
    workload: Mapped[int | None] = mapped_column(Integer, nullable=True)

    course: Mapped["Course"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"<CourseReview(id={self.id}, course_id={self.course_id}, user_id={self.user_id})>"
