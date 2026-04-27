"""notifications profile flag and reminder marker

Revision ID: 20260420_0015
Revises: 20260420_0014
Create Date: 2026-04-20 15:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_0015"
down_revision: Union[str, None] = "20260420_0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    user_cols = {c["name"] for c in sa.inspect(bind).get_columns("users")}
    job_cols = {
        c["name"]
        for c in sa.inspect(bind).get_columns("mock_exam_generation_jobs")
    }

    if "subscribed_to_notifications" not in user_cols:
        op.add_column(
            "users",
            sa.Column(
                "subscribed_to_notifications",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            ),
        )

    if "notification_sent_at" not in job_cols:
        op.add_column(
            "mock_exam_generation_jobs",
            sa.Column(
                "notification_sent_at",
                sa.DateTime(timezone=True),
                nullable=True,
            ),
        )


def downgrade() -> None:
    op.drop_column("mock_exam_generation_jobs", "notification_sent_at")
    op.drop_column("users", "subscribed_to_notifications")
