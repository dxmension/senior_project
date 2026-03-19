"""add assessments table

Revision ID: a3c7e9f2b841
Revises: 9b3f4c2d1a10
Create Date: 2026-03-19 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a3c7e9f2b841"
down_revision: Union[str, None] = "9b3f4c2d1a10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE assessment_type AS ENUM (
                'homework',
                'quiz',
                'midterm',
                'final',
                'project',
                'lab',
                'presentation',
                'other'
            );
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )
    op.create_table(
        "assessments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column(
            "assessment_type",
            postgresql.ENUM(
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
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessments_id"), "assessments", ["id"], unique=True)
    op.create_index(
        "ix_assessments_user_course",
        "assessments",
        ["user_id", "course_id"],
        unique=False,
    )
    op.create_index(
        "ix_assessments_user_deadline",
        "assessments",
        ["user_id", "deadline"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_assessments_user_deadline", table_name="assessments")
    op.drop_index("ix_assessments_user_course", table_name="assessments")
    op.drop_index(op.f("ix_assessments_id"), table_name="assessments")
    op.drop_table("assessments")
    op.execute("DROP TYPE IF EXISTS assessment_type")
