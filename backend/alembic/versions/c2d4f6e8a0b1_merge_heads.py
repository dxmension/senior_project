"""merge heads

Revision ID: c2d4f6e8a0b1
Revises: b5e8a1d3f920, 6a9275f1d8c4
Create Date: 2026-03-19 12:00:00.000000

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "c2d4f6e8a0b1"
down_revision: Union[str, tuple[str, ...]] = ("b5e8a1d3f920", "6a9275f1d8c4")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
