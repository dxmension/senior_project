"""add requirements_term and requirements_year to courses

Revision ID: a7b8c9d0e1f2
Revises: f6a7b8c9d0e5
Create Date: 2026-03-28

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a7b8c9d0e1f2"
down_revision: str | None = "f6a7b8c9d0e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("courses", sa.Column("requirements_term", sa.String(16), nullable=True))
    op.add_column("courses", sa.Column("requirements_year", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("courses", "requirements_year")
    op.drop_column("courses", "requirements_term")
