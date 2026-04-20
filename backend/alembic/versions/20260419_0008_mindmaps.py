"""mindmaps

Revision ID: 20260419_0008
Revises: 20260418_0007
Create Date: 2026-04-19 12:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260419_0008"
down_revision: Union[str, None] = "20260418_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("mindmaps"):
        return

    op.create_table(
        "mindmaps",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("week", sa.Integer(), nullable=False),
        sa.Column("topic", sa.String(length=500), nullable=False),
        sa.Column("tree_json", sa.JSON(), nullable=False),
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
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_mindmaps_id"), "mindmaps", ["id"], unique=True)
    op.create_index("ix_mindmaps_user_course", "mindmaps", ["user_id", "course_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_mindmaps_user_course", table_name="mindmaps")
    op.drop_index(op.f("ix_mindmaps_id"), table_name="mindmaps")
    op.drop_table("mindmaps")
