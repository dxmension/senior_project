"""add priority_4 to courses

Revision ID: f6a7b8c9d0e5
Revises: e5f6a7b8c9d4
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f6a7b8c9d0e5"
down_revision: str | None = "e5f6a7b8c9d4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("priority_4", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "priority_4")
