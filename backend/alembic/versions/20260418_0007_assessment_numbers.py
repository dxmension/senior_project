"""assessment numbers and generated mock exam titles

Revision ID: 20260418_0007
Revises: 20260418_0006
Create Date: 2026-04-18 22:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260418_0007"
down_revision: Union[str, None] = "20260418_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _label_sql(column: str) -> str:
    return (
        "CASE "
        f"WHEN {column}::text = 'quiz' THEN 'Quiz' "
        f"WHEN {column}::text = 'midterm' THEN 'Midterm' "
        f"WHEN {column}::text = 'final' THEN 'Final' "
        f"WHEN {column}::text = 'homework' THEN 'Homework' "
        f"WHEN {column}::text = 'project' THEN 'Project' "
        f"WHEN {column}::text = 'lab' THEN 'Lab' "
        f"WHEN {column}::text = 'presentation' THEN 'Presentation' "
        "ELSE 'Assessment' END"
    )


def upgrade() -> None:
    cols = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("assessments")}
    if "assessment_number" in cols:
        return

    op.add_column(
        "assessments",
        sa.Column("assessment_number", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                DENSE_RANK() OVER (
                    PARTITION BY user_id, course_id, assessment_type
                    ORDER BY deadline, created_at, title, id
                ) AS assessment_number
            FROM assessments
        )
        UPDATE assessments AS items
        SET assessment_number = ranked.assessment_number
        FROM ranked
        WHERE items.id = ranked.id
        """
    )
    op.alter_column("assessments", "assessment_number", nullable=False)
    op.create_unique_constraint(
        "uq_assessments_identity",
        "assessments",
        ["user_id", "course_id", "assessment_type", "assessment_number"],
    )
    op.drop_column("assessments", "title")

    label = _label_sql("assessment_type")
    op.execute(
        f"""
        UPDATE mock_exams
        SET
            assessment_title = {label} || ' ' || assessment_number::text,
            assessment_title_slug = LOWER(
                REPLACE({label} || ' ' || assessment_number::text, ' ', '-')
            ),
            title = {label}
                || ' '
                || assessment_number::text
                || ' Mock '
                || version::text
        """
    )


def downgrade() -> None:
    op.add_column(
        "assessments",
        sa.Column("title", sa.String(length=255), nullable=True),
    )
    label = _label_sql("assessment_type")
    op.execute(
        f"""
        UPDATE assessments
        SET title = {label} || ' ' || assessment_number::text
        """
    )
    op.alter_column("assessments", "title", nullable=False)
    op.drop_constraint("uq_assessments_identity", "assessments", type_="unique")
    op.drop_column("assessments", "assessment_number")

    mock_label = _label_sql("assessment_type")
    op.execute(
        f"""
        UPDATE mock_exams
        SET
            assessment_title = {mock_label} || ' ' || assessment_number::text,
            assessment_title_slug = LOWER(
                REPLACE({mock_label} || ' ' || assessment_number::text, ' ', '-')
            ),
            title = {mock_label} || ' ' || assessment_number::text || ' Mock'
        """
    )
