"""study guides

Revision ID: 20260420_0012
Revises: 20260419_0011
Create Date: 2026-04-20 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "20260420_0012"
down_revision: Union[str, None] = "20260419_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

study_guide_source_type = postgresql.ENUM(
    "materials",
    "ai_knowledge",
    "hybrid",
    name="studyguidesourcetype",
    create_type=False,
)


def upgrade() -> None:
    study_guide_source_type.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "study_guides",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=False),
        sa.Column("overview_json", sa.JSON(), nullable=False),
        sa.Column(
            "details_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'::json"),
        ),
        sa.Column("source_type", study_guide_source_type, nullable=False),
        sa.Column("materials_hash", sa.String(length=64), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["course_offerings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_study_guides_id"),
        "study_guides",
        ["id"],
        unique=True,
    )
    op.create_index(
        "ix_study_guides_user_course_topic",
        "study_guides",
        ["user_id", "course_id", "topic"],
    )

    op.create_table(
        "week_overview_cache",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("summary", sa.String(length=2000), nullable=False),
        sa.Column("topics_json", sa.JSON(), nullable=False),
        sa.Column("materials_hash", sa.String(length=64), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["course_id"], ["course_offerings.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_week_overview_cache_id"),
        "week_overview_cache",
        ["id"],
        unique=True,
    )
    op.create_index(
        "ix_week_overview_cache_user_course_week",
        "week_overview_cache",
        ["user_id", "course_id", "week"],
        unique=True,
    )


def downgrade() -> None:
    op.execute(
        "DROP INDEX IF EXISTS ix_week_overview_cache_user_course_week"
    )
    op.execute(
        "DROP INDEX IF EXISTS ix_week_overview_cache_id"
    )
    op.execute("DROP TABLE IF EXISTS week_overview_cache")
    op.drop_index(
        "ix_study_guides_user_course_topic",
        table_name="study_guides",
    )
    op.drop_index(
        op.f("ix_study_guides_id"),
        table_name="study_guides",
    )
    op.drop_table("study_guides")
    study_guide_source_type.drop(op.get_bind(), checkfirst=True)
