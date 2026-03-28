"""add priority columns to courses

Revision ID: e5f6a7b8c9d4
Revises: d4e5f6a7b8c3
Create Date: 2026-03-27

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e5f6a7b8c9d4"
down_revision: str | None = "d4e5f6a7b8c3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("priority_1", sa.Text(), nullable=True))
    op.add_column("courses", sa.Column("priority_2", sa.Text(), nullable=True))
    op.add_column("courses", sa.Column("priority_3", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "priority_3")
    op.drop_column("courses", "priority_2")
    op.drop_column("courses", "priority_1")
