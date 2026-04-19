"""add handbook_plans table and users.enrollment_year

Revision ID: 0002_handbook
Revises: 0001_squashed
Create Date: 2026-04-18
"""
from typing import Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_handbook"
down_revision: Union[str, None] = "0001_squashed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("enrollment_year", sa.Integer(), nullable=True),
    )

    op.create_table(
        "handbook_plans",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("enrollment_year", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(256), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="processing"),
        sa.Column("plans", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
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
            onupdate=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("enrollment_year", name="uq_handbook_plans_year"),
    )


def downgrade() -> None:
    op.drop_table("handbook_plans")
    op.drop_column("users", "enrollment_year")
