"""add categories and events tables

Revision ID: b5e8a1d3f920
Revises: a3c7e9f2b841
Create Date: 2026-03-19 11:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b5e8a1d3f920"
down_revision: Union[str, None] = "a3c7e9f2b841"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create recurrence_type enum
    op.execute(
        """
        DO $$
        BEGIN
            CREATE TYPE recurrence_type AS ENUM (
                'none',
                'daily',
                'weekly',
                'biweekly',
                'monthly'
            );
        EXCEPTION
            WHEN duplicate_object THEN NULL;
        END
        $$;
        """
    )

    # 2. Create categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=True)
    op.create_index("ix_categories_user_id", "categories", ["user_id"], unique=False)

    # 3. Create events table
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_all_day", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column(
            "recurrence",
            postgresql.ENUM(
                "none",
                "daily",
                "weekly",
                "biweekly",
                "monthly",
                name="recurrence_type",
                create_type=False,
            ),
            nullable=False,
            server_default="none",
        ),
        sa.Column("recurrence_end_at", sa.DateTime(timezone=True), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["category_id"], ["categories.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=True)
    op.create_index(
        "ix_events_user_start_at", "events", ["user_id", "start_at"], unique=False
    )
    op.create_index(
        "ix_events_user_category", "events", ["user_id", "category_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_events_user_category", table_name="events")
    op.drop_index("ix_events_user_start_at", table_name="events")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")
    op.drop_index("ix_categories_user_id", table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")
    op.execute("DROP TYPE IF EXISTS recurrence_type")
