"""handbook plans

Revision ID: 20260419_0010
Revises: 20260419_0009
Create Date: 2026-04-19 19:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260419_0010"
down_revision: Union[str, None] = "20260419_0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("handbook_plans"):
        return

    op.create_table(
        "handbook_plans",
        sa.Column("enrollment_year", sa.Integer(), nullable=False),
        sa.Column("filename", sa.String(length=256), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("plans", sa.JSON(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "enrollment_year",
            name="uq_handbook_plans_year",
        ),
    )
    op.create_index(
        op.f("ix_handbook_plans_id"),
        "handbook_plans",
        ["id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_handbook_plans_id"), table_name="handbook_plans")
    op.drop_table("handbook_plans")
