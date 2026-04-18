import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.assessments.models import AssessmentType
from nutrack.models import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from nutrack.courses.models import Course, CourseOffering
    from nutrack.users.models import User


class MaterialUploadStatus(str, enum.Enum):
    QUEUED = "queued"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class MaterialCurationStatus(str, enum.Enum):
    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"


class MockExamAttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MockExamQuestionSource(str, enum.Enum):
    AI = "ai"
    HISTORIC = "historic"
    RUMORED = "rumored"
    TUTOR_MADE = "tutor_made"


class StudyMaterialUpload(Base, IDMixin, TimestampMixin):
    __tablename__ = "study_material_uploads"

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_week: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    staged_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_status: Mapped[MaterialUploadStatus] = mapped_column(
        Enum(MaterialUploadStatus),
        nullable=False,
        default=MaterialUploadStatus.QUEUED,
    )
    curation_status: Mapped[MaterialCurationStatus] = mapped_column(
        Enum(MaterialCurationStatus),
        nullable=False,
        default=MaterialCurationStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    course_offering: Mapped["CourseOffering"] = relationship()
    uploader: Mapped["User"] = relationship()
    library_entry: Mapped["StudyMaterialLibraryEntry | None"] = relationship(
        back_populates="upload",
        uselist=False,
    )


class StudyMaterialLibraryEntry(Base, IDMixin, TimestampMixin):
    __tablename__ = "study_material_library_entries"
    __table_args__ = (
        UniqueConstraint("upload_id", name="uq_study_material_library_upload"),
    )

    upload_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study_material_uploads.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    curated_title: Mapped[str] = mapped_column(String(255), nullable=False)
    curated_week: Mapped[int] = mapped_column(Integer, nullable=False)
    curated_by_admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    upload: Mapped[StudyMaterialUpload] = relationship(back_populates="library_entry")
    course_offering: Mapped["CourseOffering"] = relationship()
    curated_by_admin: Mapped["User"] = relationship()


class MockExam(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exams"
    __table_args__ = (
        UniqueConstraint(
            "course_id",
            "assessment_type",
            "assessment_number",
            "version",
            name="uq_mock_exams_version",
        ),
        Index(
            "uq_mock_exams_active",
            "course_id",
            "assessment_type",
            "assessment_number",
            unique=True,
            postgresql_where=sa.text("is_active = true"),
        ),
        Index("ix_mock_exams_course_id", "course_id"),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    assessment_type: Mapped[AssessmentType] = mapped_column(
        sa.Enum(
            AssessmentType,
            name="assessment_type",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
        ),
        nullable=False,
    )
    assessment_number: Mapped[int] = mapped_column(Integer, nullable=False)
    assessment_title: Mapped[str] = mapped_column(String(255), nullable=False)
    assessment_title_slug: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    course: Mapped["Course"] = relationship()
    created_by_admin: Mapped["User"] = relationship()
    question_links: Mapped[list["MockExamQuestionLink"]] = relationship(
        back_populates="mock_exam",
        cascade="all, delete-orphan",
    )
    attempts: Mapped[list["MockExamAttempt"]] = relationship(
        back_populates="mock_exam",
        cascade="all, delete-orphan",
    )


class MockExamQuestion(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exam_questions"
    __table_args__ = (
        CheckConstraint(
            "correct_option_index BETWEEN 1 AND 6",
            name="ck_mock_exam_questions_correct_option",
        ),
        CheckConstraint(
            "(source = 'historic') "
            "OR (source IN ('ai', 'rumored', 'tutor_made') "
            "AND historical_course_offering_id IS NULL)",
            name="ck_mock_exam_questions_source_offering",
        ),
        Index("ix_mock_exam_questions_course_id", "course_id"),
        Index(
            "ix_mock_exam_questions_historical_offering_id",
            "historical_course_offering_id",
        ),
    )

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[MockExamQuestionSource] = mapped_column(
        sa.Enum(
            MockExamQuestionSource,
            name="mockexamquestionsource",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=MockExamQuestionSource.AI,
    )
    historical_course_offering_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=True,
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    answer_variant_1: Mapped[str] = mapped_column(Text, nullable=False)
    answer_variant_2: Mapped[str] = mapped_column(Text, nullable=False)
    answer_variant_3: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_variant_4: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_variant_5: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_variant_6: Mapped[str | None] = mapped_column(Text, nullable=True)
    correct_option_index: Mapped[int] = mapped_column(Integer, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    course: Mapped["Course"] = relationship()
    historical_course_offering: Mapped["CourseOffering | None"] = relationship()
    created_by_admin: Mapped["User"] = relationship()
    mock_exam_links: Mapped[list["MockExamQuestionLink"]] = relationship(
        back_populates="question",
    )


class MockExamQuestionLink(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exam_question_links"
    __table_args__ = (
        UniqueConstraint(
            "mock_exam_id",
            "position",
            name="uq_mock_exam_question_links_position",
        ),
        UniqueConstraint(
            "mock_exam_id",
            "question_id",
            name="uq_mock_exam_question_links_question",
        ),
    )

    mock_exam_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_exams.id", ondelete="CASCADE"),
        nullable=False,
    )
    question_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_exam_questions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    points: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    mock_exam: Mapped[MockExam] = relationship(back_populates="question_links")
    question: Mapped[MockExamQuestion] = relationship(back_populates="mock_exam_links")
    answers: Mapped[list["MockExamAttemptAnswer"]] = relationship(
        back_populates="question_link",
    )


class MockExamAttempt(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exam_attempts"
    __table_args__ = (
        Index("ix_mock_exam_attempts_user_id", "user_id"),
        Index("ix_mock_exam_attempts_mock_exam_id", "mock_exam_id"),
        Index(
            "uq_mock_exam_attempts_active",
            "user_id",
            "mock_exam_id",
            unique=True,
            postgresql_where=sa.text("status = 'IN_PROGRESS'"),
        ),
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    mock_exam_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_exams.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[MockExamAttemptStatus] = mapped_column(
        Enum(MockExamAttemptStatus),
        nullable=False,
        default=MockExamAttemptStatus.IN_PROGRESS,
    )
    started_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    submitted_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    last_active_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True))
    current_position: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    answered_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    score_pct: Mapped[float | None] = mapped_column(Float, nullable=True)

    user: Mapped["User"] = relationship()
    mock_exam: Mapped[MockExam] = relationship(back_populates="attempts")
    answers: Mapped[list["MockExamAttemptAnswer"]] = relationship(
        back_populates="attempt",
        cascade="all, delete-orphan",
    )


class MockExamAttemptAnswer(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exam_attempt_answers"
    __table_args__ = (
        UniqueConstraint(
            "attempt_id",
            "mock_exam_question_link_id",
            name="uq_mock_exam_attempt_answers_link",
        ),
        CheckConstraint(
            "selected_option_index IS NULL OR selected_option_index BETWEEN 1 AND 6",
            name="ck_mock_exam_attempt_answers_selected_option",
        ),
    )

    attempt_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_exam_attempts.id", ondelete="CASCADE"),
        nullable=False,
    )
    mock_exam_question_link_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("mock_exam_question_links.id", ondelete="CASCADE"),
        nullable=False,
    )
    selected_option_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )

    attempt: Mapped[MockExamAttempt] = relationship(back_populates="answers")
    question_link: Mapped[MockExamQuestionLink] = relationship(back_populates="answers")
