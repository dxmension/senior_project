"""add historic_section and historic_year to mock_exam_questions

Revision ID: 20260420_0016
Revises: 20260420_0015
Create Date: 2026-04-20 16:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_0016"
down_revision: Union[str, None] = "20260420_0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "mock_exam_questions",
        sa.Column("historic_section", sa.String(100), nullable=True),
    )
    op.add_column(
        "mock_exam_questions",
        sa.Column("historic_year", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("mock_exam_questions", "historic_year")
    op.drop_column("mock_exam_questions", "historic_section")
