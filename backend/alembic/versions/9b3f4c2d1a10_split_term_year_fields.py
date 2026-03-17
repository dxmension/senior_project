"""split semester into term and year

Revision ID: 9b3f4c2d1a10
Revises: 4f7d2b1a9c33
Create Date: 2026-03-17 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


revision: str = "9b3f4c2d1a10"
down_revision: Union[str, None] = "4f7d2b1a9c33"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("term", sa.String(length=16), nullable=True))
    op.add_column("courses", sa.Column("year", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE courses
        SET term = 'Spring', year = 2026
        WHERE term IS NULL OR year IS NULL
        """
    )
    op.alter_column("courses", "term", nullable=False)
    op.alter_column("courses", "year", nullable=False)
    op.drop_constraint(
        "uq_courses_code_level_section",
        "courses",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_courses_code_level_section_term_year",
        "courses",
        ["code", "level", "section", "term", "year"],
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM enrollments
                WHERE semester !~ '^(Spring|Summer|Fall) [0-9]{4}$'
            ) THEN
                RAISE EXCEPTION 'Invalid semester value found in enrollments';
            END IF;
        END
        $$;
        """
    )
    op.add_column(
        "enrollments",
        sa.Column("term", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "enrollments",
        sa.Column("year", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        UPDATE enrollments
        SET term = split_part(semester, ' ', 1),
            year = CAST(split_part(semester, ' ', 2) AS INTEGER)
        """
    )
    op.alter_column("enrollments", "term", nullable=False)
    op.alter_column("enrollments", "year", nullable=False)
    op.drop_constraint("pk_enrollments", "enrollments", type_="primary")
    op.create_primary_key(
        "pk_enrollments",
        "enrollments",
        ["user_id", "course_id", "term", "year"],
    )
    op.drop_column("enrollments", "semester")


def downgrade() -> None:
    op.add_column(
        "enrollments",
        sa.Column("semester", sa.String(length=16), nullable=True),
    )
    op.execute(
        """
        UPDATE enrollments
        SET semester = term || ' ' || year
        """
    )
    op.alter_column("enrollments", "semester", nullable=False)
    op.drop_constraint("pk_enrollments", "enrollments", type_="primary")
    op.create_primary_key(
        "pk_enrollments",
        "enrollments",
        ["user_id", "course_id", "semester"],
    )
    op.drop_column("enrollments", "year")
    op.drop_column("enrollments", "term")

    op.drop_constraint(
        "uq_courses_code_level_section_term_year",
        "courses",
        type_="unique",
    )
    op.execute(
        """
        DELETE FROM courses c
        USING (
            SELECT
                id,
                row_number() OVER (
                    PARTITION BY code, level, section
                    ORDER BY year DESC,
                        CASE term
                            WHEN 'Fall' THEN 3
                            WHEN 'Summer' THEN 2
                            WHEN 'Spring' THEN 1
                            ELSE 0
                        END DESC,
                        id DESC
                ) AS row_num
            FROM courses
        ) ranked
        WHERE c.id = ranked.id
          AND ranked.row_num > 1
        """
    )
    op.create_unique_constraint(
        "uq_courses_code_level_section",
        "courses",
        ["code", "level", "section"],
    )
    op.drop_column("courses", "year")
    op.drop_column("courses", "term")
