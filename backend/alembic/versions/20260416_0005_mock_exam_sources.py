"""mock exam course-wide scope and question sources

Revision ID: 20260416_0005
Revises: 20260416_0004
Create Date: 2026-04-16 18:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260416_0005"
down_revision: Union[str, None] = "20260416_0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

question_source = postgresql.ENUM(
    "ai",
    "historic",
    "rumored",
    "tutor_made",
    name="mockexamquestionsource",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    question_source.create(bind, checkfirst=True)

    op.execute("DROP INDEX IF EXISTS uq_mock_exams_active_by_offering")
    op.execute("DROP INDEX IF EXISTS uq_mock_exams_active_all_sections")
    op.execute("DROP INDEX IF EXISTS ix_mock_exams_offering_id")
    op.execute("ALTER TABLE mock_exams DROP CONSTRAINT IF EXISTS uq_mock_exams_version")
    op.execute("ALTER TABLE mock_exams DROP COLUMN IF EXISTS course_offering_id CASCADE")
    op.create_unique_constraint(
        "uq_mock_exams_version",
        "mock_exams",
        ["course_id", "assessment_type", "assessment_title_slug", "version"],
    )
    op.create_index(
        "uq_mock_exams_active",
        "mock_exams",
        ["course_id", "assessment_type", "assessment_title_slug"],
        unique=True,
        postgresql_where=sa.text("is_active = true"),
    )

    op.execute("DROP INDEX IF EXISTS ix_mock_exam_questions_offering_id")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'mock_exam_questions'
                AND column_name = 'course_offering_id'
            ) THEN
                ALTER TABLE mock_exam_questions
                RENAME COLUMN course_offering_id TO historical_course_offering_id;
            END IF;
        END $$;
        """
    )
    op.add_column(
        "mock_exam_questions",
        sa.Column(
            "source",
            question_source,
            nullable=True,
            server_default=sa.text("'ai'"),
        ),
    )
    op.execute(
        """
        UPDATE mock_exam_questions
        SET source = CASE
            WHEN historical_course_offering_id IS NULL THEN 'ai'
            ELSE 'historic'
        END::mockexamquestionsource
        """
    )
    op.alter_column(
        "mock_exam_questions",
        "source",
        existing_type=question_source,
        nullable=False,
        server_default=None,
    )
    op.create_index(
        "ix_mock_exam_questions_historical_offering_id",
        "mock_exam_questions",
        ["historical_course_offering_id"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_mock_exam_questions_source_offering",
        "mock_exam_questions",
        "(source = 'historic') "
        "OR (source IN ('ai', 'rumored', 'tutor_made') "
        "AND historical_course_offering_id IS NULL)",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_mock_exam_questions_source_offering",
        "mock_exam_questions",
        type_="check",
    )
    op.drop_index(
        "ix_mock_exam_questions_historical_offering_id",
        table_name="mock_exam_questions",
    )
    op.drop_column("mock_exam_questions", "source")
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM information_schema.columns
                WHERE table_name = 'mock_exam_questions'
                AND column_name = 'historical_course_offering_id'
            ) THEN
                ALTER TABLE mock_exam_questions
                RENAME COLUMN historical_course_offering_id TO course_offering_id;
            END IF;
        END $$;
        """
    )
    op.create_index(
        "ix_mock_exam_questions_offering_id",
        "mock_exam_questions",
        ["course_offering_id"],
        unique=False,
    )

    op.drop_index("uq_mock_exams_active", table_name="mock_exams")
    op.execute("ALTER TABLE mock_exams DROP CONSTRAINT IF EXISTS uq_mock_exams_version")
    op.add_column(
        "mock_exams",
        sa.Column("course_offering_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "mock_exams_course_offering_id_fkey",
        "mock_exams",
        "course_offerings",
        ["course_offering_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_unique_constraint(
        "uq_mock_exams_version",
        "mock_exams",
        [
            "course_id",
            "course_offering_id",
            "assessment_type",
            "assessment_title_slug",
            "version",
        ],
    )
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

    question_source.drop(op.get_bind(), checkfirst=True)
