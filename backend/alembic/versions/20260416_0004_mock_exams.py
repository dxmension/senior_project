"""mock exams

Revision ID: 20260416_0004
Revises: 20260414_0003
Create Date: 2026-04-16 16:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260416_0004"
down_revision: Union[str, None] = "20260414_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

assessment_type = postgresql.ENUM(
    "homework",
    "quiz",
    "midterm",
    "final",
    "project",
    "lab",
    "presentation",
    "other",
    name="assessment_type",
    create_type=False,
)
mock_exam_attempt_status = postgresql.ENUM(
    "IN_PROGRESS",
    "COMPLETED",
    "ABANDONED",
    name="mockexamattemptstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    assessment_type.create(bind, checkfirst=True)
    mock_exam_attempt_status.create(bind, checkfirst=True)

    existing = set(sa.inspect(bind).get_table_names())
    if "mock_exams" in existing:
        return

    op.create_table(
        "mock_exams",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("course_offering_id", sa.Integer(), nullable=True),
        sa.Column("assessment_type", assessment_type, nullable=False),
        sa.Column("assessment_title", sa.String(length=255), nullable=False),
        sa.Column("assessment_title_slug", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=True),
        sa.Column("instructions", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_by_admin_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["course_offering_id"],
            ["course_offerings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "course_offering_id",
            "assessment_type",
            "assessment_title_slug",
            "version",
            name="uq_mock_exams_version",
        ),
    )
    op.create_index(op.f("ix_mock_exams_id"), "mock_exams", ["id"], unique=True)
    op.create_index("ix_mock_exams_course_id", "mock_exams", ["course_id"], unique=False)
    op.create_index(
        "ix_mock_exams_offering_id",
        "mock_exams",
        ["course_offering_id"],
        unique=False,
    )
    op.create_index(
        "uq_mock_exams_active_by_offering",
        "mock_exams",
        ["course_offering_id", "assessment_type", "assessment_title_slug"],
        unique=True,
        postgresql_where=sa.text("is_active = true AND course_offering_id IS NOT NULL"),
    )
    op.create_index(
        "uq_mock_exams_active_all_sections",
        "mock_exams",
        ["course_id", "assessment_type", "assessment_title_slug"],
        unique=True,
        postgresql_where=sa.text("is_active = true AND course_offering_id IS NULL"),
    )

    op.create_table(
        "mock_exam_questions",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("course_offering_id", sa.Integer(), nullable=True),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("answer_variant_1", sa.Text(), nullable=False),
        sa.Column("answer_variant_2", sa.Text(), nullable=False),
        sa.Column("answer_variant_3", sa.Text(), nullable=True),
        sa.Column("answer_variant_4", sa.Text(), nullable=True),
        sa.Column("answer_variant_5", sa.Text(), nullable=True),
        sa.Column("answer_variant_6", sa.Text(), nullable=True),
        sa.Column("correct_option_index", sa.Integer(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=True),
        sa.Column("created_by_admin_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "correct_option_index BETWEEN 1 AND 6",
            name="ck_mock_exam_questions_correct_option",
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["course_offering_id"],
            ["course_offerings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["created_by_admin_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mock_exam_questions_id"),
        "mock_exam_questions",
        ["id"],
        unique=True,
    )
    op.create_index(
        "ix_mock_exam_questions_course_id",
        "mock_exam_questions",
        ["course_id"],
        unique=False,
    )
    op.create_index(
        "ix_mock_exam_questions_offering_id",
        "mock_exam_questions",
        ["course_offering_id"],
        unique=False,
    )

    op.create_table(
        "mock_exam_question_links",
        sa.Column("mock_exam_id", sa.Integer(), nullable=False),
        sa.Column("question_id", sa.Integer(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["mock_exam_id"], ["mock_exams.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["mock_exam_questions.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "mock_exam_id",
            "position",
            name="uq_mock_exam_question_links_position",
        ),
        sa.UniqueConstraint(
            "mock_exam_id",
            "question_id",
            name="uq_mock_exam_question_links_question",
        ),
    )
    op.create_index(
        op.f("ix_mock_exam_question_links_id"),
        "mock_exam_question_links",
        ["id"],
        unique=True,
    )

    op.create_table(
        "mock_exam_attempts",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("mock_exam_id", sa.Integer(), nullable=False),
        sa.Column("status", mock_exam_attempt_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("current_position", sa.Integer(), nullable=False),
        sa.Column("answered_count", sa.Integer(), nullable=False),
        sa.Column("correct_count", sa.Integer(), nullable=False),
        sa.Column("score_pct", sa.Float(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["mock_exam_id"], ["mock_exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mock_exam_attempts_id"),
        "mock_exam_attempts",
        ["id"],
        unique=True,
    )
    op.create_index(
        "ix_mock_exam_attempts_user_id",
        "mock_exam_attempts",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_mock_exam_attempts_mock_exam_id",
        "mock_exam_attempts",
        ["mock_exam_id"],
        unique=False,
    )
    op.create_index(
        "uq_mock_exam_attempts_active",
        "mock_exam_attempts",
        ["user_id", "mock_exam_id"],
        unique=True,
        postgresql_where=sa.text("status = 'IN_PROGRESS'"),
    )

    op.create_table(
        "mock_exam_attempt_answers",
        sa.Column("attempt_id", sa.Integer(), nullable=False),
        sa.Column("mock_exam_question_link_id", sa.Integer(), nullable=False),
        sa.Column("selected_option_index", sa.Integer(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=True),
        sa.Column("answered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "selected_option_index IS NULL OR selected_option_index BETWEEN 1 AND 6",
            name="ck_mock_exam_attempt_answers_selected_option",
        ),
        sa.ForeignKeyConstraint(
            ["attempt_id"],
            ["mock_exam_attempts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["mock_exam_question_link_id"],
            ["mock_exam_question_links.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "attempt_id",
            "mock_exam_question_link_id",
            name="uq_mock_exam_attempt_answers_link",
        ),
    )
    op.create_index(
        op.f("ix_mock_exam_attempt_answers_id"),
        "mock_exam_attempt_answers",
        ["id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_mock_exam_attempt_answers_id"), table_name="mock_exam_attempt_answers")
    op.drop_table("mock_exam_attempt_answers")
    op.drop_index("uq_mock_exam_attempts_active", table_name="mock_exam_attempts")
    op.drop_index("ix_mock_exam_attempts_mock_exam_id", table_name="mock_exam_attempts")
    op.drop_index("ix_mock_exam_attempts_user_id", table_name="mock_exam_attempts")
    op.drop_index(op.f("ix_mock_exam_attempts_id"), table_name="mock_exam_attempts")
    op.drop_table("mock_exam_attempts")
    op.drop_index(op.f("ix_mock_exam_question_links_id"), table_name="mock_exam_question_links")
    op.drop_table("mock_exam_question_links")
    op.drop_index("ix_mock_exam_questions_offering_id", table_name="mock_exam_questions")
    op.drop_index("ix_mock_exam_questions_course_id", table_name="mock_exam_questions")
    op.drop_index(op.f("ix_mock_exam_questions_id"), table_name="mock_exam_questions")
    op.drop_table("mock_exam_questions")
    op.drop_index("uq_mock_exams_active_all_sections", table_name="mock_exams")
    op.drop_index("uq_mock_exams_active_by_offering", table_name="mock_exams")
    op.drop_index("ix_mock_exams_offering_id", table_name="mock_exams")
    op.drop_index("ix_mock_exams_course_id", table_name="mock_exams")
    op.drop_index(op.f("ix_mock_exams_id"), table_name="mock_exams")
    op.drop_table("mock_exams")
    mock_exam_attempt_status.drop(op.get_bind(), checkfirst=True)
