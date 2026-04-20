"""mock exam generation options

Revision ID: 20260419_0012
Revises: 20260419_0011
Create Date: 2026-04-19 19:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260419_0012"
down_revision: Union[str, None] = "20260419_0011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mock_exam_generation_jobs",
        sa.Column("generation_options", sa.Text(), nullable=True),
    )
    op.add_column(
        "mock_exams",
        sa.Column("difficulty", sa.String(16), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("mock_exam_generation_jobs", "generation_options")
    op.drop_column("mock_exams", "difficulty")
