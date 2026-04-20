"""mock exam ai generation

Revision ID: 20260419_0011
Revises: 20260419_0010
Create Date: 2026-04-19 18:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260419_0011"
down_revision: Union[str, None] = "20260419_0010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

mock_exam_origin = postgresql.ENUM(
    "manual",
    "ai",
    name="mockexamorigin",
    create_type=False,
)
mock_exam_visibility_scope = postgresql.ENUM(
    "course",
    "personal",
    name="mockexamvisibilityscope",
    create_type=False,
)
mock_exam_generation_trigger = postgresql.ENUM(
    "create",
    "update",
    "deadline_reminder",
    "retry",
    name="mockexamgenerationtrigger",
    create_type=False,
)
mock_exam_generation_status = postgresql.ENUM(
    "queued",
    "running",
    "completed",
    "failed",
    "cancelled",
    "skipped",
    name="mockexamgenerationstatus",
    create_type=False,
)
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


def upgrade() -> None:
    bind = op.get_bind()
    mock_exam_origin.create(bind, checkfirst=True)
    mock_exam_visibility_scope.create(bind, checkfirst=True)
    mock_exam_generation_trigger.create(bind, checkfirst=True)
    mock_exam_generation_status.create(bind, checkfirst=True)

    op.add_column(
        "mock_exams",
        sa.Column(
            "origin",
            mock_exam_origin,
            nullable=True,
            server_default=sa.text("'manual'"),
        ),
    )
    op.add_column(
        "mock_exams",
        sa.Column(
            "visibility_scope",
            mock_exam_visibility_scope,
            nullable=True,
            server_default=sa.text("'course'"),
        ),
    )
    op.add_column("mock_exams", sa.Column("owner_user_id", sa.Integer(), nullable=True))
    op.add_column("mock_exams", sa.Column("assessment_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "mock_exams_owner_user_id_fkey",
        "mock_exams",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "mock_exams_assessment_id_fkey",
        "mock_exams",
        "assessments",
        ["assessment_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        """
        UPDATE mock_exams
        SET
            origin = 'manual'::mockexamorigin,
            visibility_scope = 'course'::mockexamvisibilityscope
        """
    )
    op.alter_column("mock_exams", "origin", nullable=False, server_default=None)
    op.alter_column(
        "mock_exams",
        "visibility_scope",
        nullable=False,
        server_default=None,
    )

    op.add_column(
        "mock_exam_questions",
        sa.Column(
            "visibility_scope",
            mock_exam_visibility_scope,
            nullable=True,
            server_default=sa.text("'course'"),
        ),
    )
    op.add_column(
        "mock_exam_questions",
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "mock_exam_questions_owner_user_id_fkey",
        "mock_exam_questions",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.execute(
        """
        UPDATE mock_exam_questions
        SET visibility_scope = 'course'::mockexamvisibilityscope
        """
    )
    op.alter_column(
        "mock_exam_questions",
        "visibility_scope",
        nullable=False,
        server_default=None,
    )

    op.execute("DROP INDEX IF EXISTS uq_mock_exams_active")
    op.execute(
        "ALTER TABLE mock_exams DROP CONSTRAINT IF EXISTS uq_mock_exams_version"
    )
    op.create_index(
        "uq_mock_exams_version_course",
        "mock_exams",
        [
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            "version",
        ],
        unique=True,
        postgresql_where=sa.text("visibility_scope = 'course'"),
    )
    op.create_index(
        "uq_mock_exams_version_personal",
        "mock_exams",
        [
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            "owner_user_id",
            "version",
        ],
        unique=True,
        postgresql_where=sa.text("visibility_scope = 'personal'"),
    )
    op.create_index(
        "uq_mock_exams_active_course",
        "mock_exams",
        ["course_id", "assessment_type", "assessment_number", "origin"],
        unique=True,
        postgresql_where=sa.text(
            "is_active = true AND visibility_scope = 'course'"
        ),
    )
    op.create_index(
        "uq_mock_exams_active_personal",
        "mock_exams",
        [
            "course_id",
            "assessment_type",
            "assessment_number",
            "origin",
            "owner_user_id",
        ],
        unique=True,
        postgresql_where=sa.text(
            "is_active = true AND visibility_scope = 'personal'"
        ),
    )

    op.create_table(
        "mock_exam_generation_settings",
        sa.Column("setting_key", sa.String(length=32), nullable=False),
        sa.Column("assessment_type", assessment_type, nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("model", sa.String(length=64), nullable=False),
        sa.Column("temperature", sa.Float(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("time_limit_minutes", sa.Integer(), nullable=True),
        sa.Column("max_source_files", sa.Integer(), nullable=False),
        sa.Column("max_source_chars", sa.Integer(), nullable=False),
        sa.Column("regeneration_offset_hours", sa.Integer(), nullable=False),
        sa.Column("new_question_ratio", sa.Float(), nullable=False),
        sa.Column("tricky_question_ratio", sa.Float(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "setting_key",
            name="uq_mock_exam_generation_settings_key",
        ),
    )
    op.create_index(
        op.f("ix_mock_exam_generation_settings_id"),
        "mock_exam_generation_settings",
        ["id"],
        unique=True,
    )

    op.create_table(
        "mock_exam_generation_jobs",
        sa.Column("assessment_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_offering_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("assessment_type", assessment_type, nullable=False),
        sa.Column("assessment_number", sa.Integer(), nullable=False),
        sa.Column("trigger", mock_exam_generation_trigger, nullable=False),
        sa.Column("status", mock_exam_generation_status, nullable=False),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("celery_task_id", sa.String(length=255), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("generated_mock_exam_id", sa.Integer(), nullable=True),
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
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["course_offering_id"],
            ["course_offerings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["generated_mock_exam_id"],
            ["mock_exams.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_mock_exam_generation_jobs_id"),
        "mock_exam_generation_jobs",
        ["id"],
        unique=True,
    )
    op.create_index(
        "ix_mock_exam_generation_jobs_assessment",
        "mock_exam_generation_jobs",
        ["assessment_id"],
        unique=False,
    )
    op.create_index(
        "ix_mock_exam_generation_jobs_status_run_at",
        "mock_exam_generation_jobs",
        ["status", "run_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_mock_exam_generation_jobs_status_run_at",
        table_name="mock_exam_generation_jobs",
    )
    op.drop_index(
        "ix_mock_exam_generation_jobs_assessment",
        table_name="mock_exam_generation_jobs",
    )
    op.drop_index(
        op.f("ix_mock_exam_generation_jobs_id"),
        table_name="mock_exam_generation_jobs",
    )
    op.drop_table("mock_exam_generation_jobs")

    op.drop_index(
        op.f("ix_mock_exam_generation_settings_id"),
        table_name="mock_exam_generation_settings",
    )
    op.drop_table("mock_exam_generation_settings")

    op.drop_index("uq_mock_exams_active_personal", table_name="mock_exams")
    op.drop_index("uq_mock_exams_active_course", table_name="mock_exams")
    op.drop_index("uq_mock_exams_version_personal", table_name="mock_exams")
    op.drop_index("uq_mock_exams_version_course", table_name="mock_exams")
    op.create_unique_constraint(
        "uq_mock_exams_version",
        "mock_exams",
        ["course_id", "assessment_type", "assessment_number", "version"],
    )
    op.create_index(
        "uq_mock_exams_active",
        "mock_exams",
        ["course_id", "assessment_type", "assessment_number"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    op.drop_constraint(
        "mock_exam_questions_owner_user_id_fkey",
        "mock_exam_questions",
        type_="foreignkey",
    )
    op.drop_column("mock_exam_questions", "owner_user_id")
    op.drop_column("mock_exam_questions", "visibility_scope")

    op.drop_constraint(
        "mock_exams_assessment_id_fkey",
        "mock_exams",
        type_="foreignkey",
    )
    op.drop_constraint(
        "mock_exams_owner_user_id_fkey",
        "mock_exams",
        type_="foreignkey",
    )
    op.drop_column("mock_exams", "assessment_id")
    op.drop_column("mock_exams", "owner_user_id")
    op.drop_column("mock_exams", "visibility_scope")
    op.drop_column("mock_exams", "origin")

    mock_exam_generation_status.drop(op.get_bind(), checkfirst=True)
    mock_exam_generation_trigger.drop(op.get_bind(), checkfirst=True)
    mock_exam_visibility_scope.drop(op.get_bind(), checkfirst=True)
    mock_exam_origin.drop(op.get_bind(), checkfirst=True)
