"""users profile columns

Revision ID: 20260419_0009
Revises: 20260419_0008
Create Date: 2026-04-19 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260419_0009"
down_revision: Union[str, None] = "20260419_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    cols = {c["name"] for c in sa.inspect(op.get_bind()).get_columns("users")}
    if "kazakh_level" not in cols:
        op.add_column("users", sa.Column("kazakh_level", sa.String(length=8), nullable=True))
    if "enrollment_year" not in cols:
        op.add_column("users", sa.Column("enrollment_year", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "enrollment_year")
    op.drop_column("users", "kazakh_level")
