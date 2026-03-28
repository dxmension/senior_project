"""add corequisites column to courses

Revision ID: c3d4e5f6a7b2
Revises: b2c3d4e5f6a1
Create Date: 2026-03-26

Adds:
  - corequisites (Text, nullable) column to the courses table,
    mirroring the existing prerequisites column.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "c3d4e5f6a7b2"
down_revision: str | None = "b2c3d4e5f6a1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("corequisites", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "corequisites")
