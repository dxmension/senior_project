import enum
from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import (
    Boolean,
    CheckConstraint,
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


class MockExamAttemptStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class MockExamQuestionSource(str, enum.Enum):
    AI = "ai"
    HISTORIC = "historic"
    RUMORED = "rumored"
    TUTOR_MADE = "tutor_made"


class MockExamQuestionCurationStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MockExamOrigin(str, enum.Enum):
    MANUAL = "manual"
    AI = "ai"


class MockExamVisibilityScope(str, enum.Enum):
    COURSE = "course"
    PERSONAL = "personal"


class MockExamGenerationTrigger(str, enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DEADLINE_REMINDER = "deadline_reminder"
    RETRY = "retry"


class MockExamDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MockExamGenerationStatus(str, enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"


class MockExam(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exams"
    __table_args__ = (
        Index(
            "uq_mock_exams_version_course",
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            "version",
            unique=True,
            postgresql_where=sa.text("visibility_scope = 'course'"),
        ),
        Index(
            "uq_mock_exams_version_personal",
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            "owner_user_id",
            "version",
            unique=True,
            postgresql_where=sa.text("visibility_scope = 'personal'"),
        ),
        Index(
            "uq_mock_exams_active_course",
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            unique=True,
            postgresql_where=sa.text(
                "is_active = true AND visibility_scope = 'course'"
            ),
        ),
        Index(
            "uq_mock_exams_active_personal",
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            "owner_user_id",
            unique=True,
            postgresql_where=sa.text(
                "is_active = true AND visibility_scope = 'personal'"
            ),
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
    origin: Mapped[MockExamOrigin] = mapped_column(
        sa.Enum(
            MockExamOrigin,
            name="mockexamorigin",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=MockExamOrigin.MANUAL,
    )
    visibility_scope: Mapped[MockExamVisibilityScope] = mapped_column(
        sa.Enum(
            MockExamVisibilityScope,
            name="mockexamvisibilityscope",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=MockExamVisibilityScope.COURSE,
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    assessment_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("assessments.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by_admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    course: Mapped["Course"] = relationship()
    created_by_admin: Mapped["User"] = relationship(
        foreign_keys=[created_by_admin_id]
    )
    owner_user: Mapped["User | None"] = relationship(foreign_keys=[owner_user_id])
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
    historic_section: Mapped[str | None] = mapped_column(String(100), nullable=True)
    historic_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
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
    visibility_scope: Mapped[MockExamVisibilityScope] = mapped_column(
        sa.Enum(
            MockExamVisibilityScope,
            name="mockexamvisibilityscope",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
        ),
        nullable=False,
        default=MockExamVisibilityScope.COURSE,
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    created_by_admin_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    submitted_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True,
    )
    curation_status: Mapped[MockExamQuestionCurationStatus] = mapped_column(
        sa.Enum(
            MockExamQuestionCurationStatus,
            name="mockexamquestioncurationstatus",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=MockExamQuestionCurationStatus.APPROVED,
    )
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    course: Mapped["Course"] = relationship()
    historical_course_offering: Mapped["CourseOffering | None"] = relationship()
    created_by_admin: Mapped["User | None"] = relationship(
        foreign_keys=[created_by_admin_id]
    )
    submitted_by_user: Mapped["User | None"] = relationship(
        foreign_keys=[submitted_by_user_id]
    )
    owner_user: Mapped["User | None"] = relationship(foreign_keys=[owner_user_id])
    mock_exam_links: Mapped[list["MockExamQuestionLink"]] = relationship(
        back_populates="question"
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
        back_populates="question_link"
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
        sa.Enum(MockExamAttemptStatus),
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


class MockExamGenerationSettings(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exam_generation_settings"
    __table_args__ = (
        UniqueConstraint("setting_key", name="uq_mock_exam_generation_settings_key"),
    )

    setting_key: Mapped[str] = mapped_column(String(32), nullable=False)
    assessment_type: Mapped[AssessmentType | None] = mapped_column(
        sa.Enum(
            AssessmentType,
            name="assessment_type",
            values_callable=lambda obj: [e.value for e in obj],
            create_type=False,
        ),
        nullable=True,
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    model: Mapped[str] = mapped_column(String(64), nullable=False)
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.2)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    max_source_files: Mapped[int] = mapped_column(Integer, nullable=False, default=6)
    max_source_chars: Mapped[int] = mapped_column(Integer, nullable=False, default=24000)
    regeneration_offset_hours: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=24,
    )
    new_question_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.5)
    tricky_question_ratio: Mapped[float] = mapped_column(Float, nullable=False, default=0.3)


class MockExamGenerationJob(Base, IDMixin, TimestampMixin):
    __tablename__ = "mock_exam_generation_jobs"
    __table_args__ = (
        Index("ix_mock_exam_generation_jobs_assessment", "assessment_id"),
        Index("ix_mock_exam_generation_jobs_status_run_at", "status", "run_at"),
    )

    assessment_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("assessments.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_offering_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
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
    trigger: Mapped[MockExamGenerationTrigger] = mapped_column(
        sa.Enum(
            MockExamGenerationTrigger,
            name="mockexamgenerationtrigger",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
    )
    status: Mapped[MockExamGenerationStatus] = mapped_column(
        sa.Enum(
            MockExamGenerationStatus,
            name="mockexamgenerationstatus",
            values_callable=lambda obj: [e.value for e in obj],
        ),
        nullable=False,
        default=MockExamGenerationStatus.QUEUED,
    )
    run_at: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    generation_options: Mapped[str | None] = mapped_column(Text, nullable=True)
    notification_sent_at: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=True,
    )
    generated_mock_exam_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("mock_exams.id", ondelete="SET NULL"),
        nullable=True,
    )
