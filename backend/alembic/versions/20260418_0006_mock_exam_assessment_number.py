"""mock exam assessment numbers

Revision ID: 20260418_0006
Revises: 20260416_0005
Create Date: 2026-04-18 20:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260418_0006"
down_revision: Union[str, None] = "20260416_0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    cols = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("mock_exams")}
    if "assessment_number" in cols:
        return

    op.add_column(
        "mock_exams",
        sa.Column("assessment_number", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        WITH family_keys AS (
            SELECT
                course_id,
                assessment_type,
                assessment_title_slug,
                MIN(created_at) AS first_created_at
            FROM mock_exams
            GROUP BY course_id, assessment_type, assessment_title_slug
        ),
        ranked AS (
            SELECT
                course_id,
                assessment_type,
                assessment_title_slug,
                DENSE_RANK() OVER (
                    PARTITION BY course_id, assessment_type
                    ORDER BY first_created_at, assessment_title_slug
                ) AS assessment_number
            FROM family_keys
        )
        UPDATE mock_exams AS exams
        SET assessment_number = ranked.assessment_number
        FROM ranked
        WHERE exams.course_id = ranked.course_id
          AND exams.assessment_type = ranked.assessment_type
          AND exams.assessment_title_slug = ranked.assessment_title_slug
        """
    )
    op.alter_column("mock_exams", "assessment_number", nullable=False)
    op.drop_index("uq_mock_exams_active", table_name="mock_exams")
    op.drop_constraint("uq_mock_exams_version", "mock_exams", type_="unique")
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


def downgrade() -> None:
    op.drop_index("uq_mock_exams_active", table_name="mock_exams")
    op.drop_constraint("uq_mock_exams_version", "mock_exams", type_="unique")
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
    op.drop_column("mock_exams", "assessment_number")
