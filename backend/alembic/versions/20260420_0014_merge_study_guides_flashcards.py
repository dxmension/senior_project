"""merge study guides and flashcards heads

Revision ID: 20260420_0014
Revises: 20260420_0012, 20260420_0013
Create Date: 2026-04-20 18:30:00.000000

"""

from typing import Sequence, Union


revision: str = "20260420_0014"
down_revision: Union[str, Sequence[str], None] = (
    "20260420_0012",
    "20260420_0013",
)
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
