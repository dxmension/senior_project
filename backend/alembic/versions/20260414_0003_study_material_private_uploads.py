"""study material private uploads

Revision ID: 20260414_0003
Revises: 20260412_0002
Create Date: 2026-04-14 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "20260414_0003"
down_revision: Union[str, None] = "20260412_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE materialcurationstatus ADD VALUE IF NOT EXISTS 'NOT_REQUESTED'"
    )


def downgrade() -> None:
    pass
