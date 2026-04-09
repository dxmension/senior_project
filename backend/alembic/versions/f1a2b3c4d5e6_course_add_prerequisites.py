"""course: add prerequisites column

Revision ID: f1a2b3c4d5e6
Revises: e1f4c6a9b712
Create Date: 2026-03-23

Adds:
  - courses.prerequisites  TEXT nullable
    Stores free-text prerequisite description uploaded from the NU course catalog.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "f1a2b3c4d5e6"
down_revision: str | None = "6a9275f1d8c4"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.add_column(
        "courses",
        sa.Column("prerequisites", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("courses", "prerequisites")
