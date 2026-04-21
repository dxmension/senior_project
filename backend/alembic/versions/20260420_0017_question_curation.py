"""add curation fields to mock_exam_questions

Revision ID: 20260420_0017
Revises: 20260420_0016
Create Date: 2026-04-20 17:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_0017"
down_revision: Union[str, None] = "20260420_0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE mockexamquestioncurationstatus AS ENUM ('pending', 'approved', 'rejected')"
    )
    op.add_column(
        "mock_exam_questions",
        sa.Column(
            "curation_status",
            sa.Enum(
                "pending",
                "approved",
                "rejected",
                name="mockexamquestioncurationstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="approved",
        ),
    )
    op.add_column(
        "mock_exam_questions",
        sa.Column("submitted_by_user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "mock_exam_questions",
        sa.Column("rejection_reason", sa.Text(), nullable=True),
    )
    op.create_foreign_key(
        "fk_mock_exam_questions_submitted_by_user",
        "mock_exam_questions",
        "users",
        ["submitted_by_user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_mock_exam_questions_curation_status",
        "mock_exam_questions",
        ["curation_status"],
    )
    op.alter_column("mock_exam_questions", "created_by_admin_id", nullable=True)


def downgrade() -> None:
    op.drop_index("ix_mock_exam_questions_curation_status", "mock_exam_questions")
    op.drop_constraint(
        "fk_mock_exam_questions_submitted_by_user", "mock_exam_questions", type_="foreignkey"
    )
    op.drop_column("mock_exam_questions", "rejection_reason")
    op.drop_column("mock_exam_questions", "submitted_by_user_id")
    op.drop_column("mock_exam_questions", "curation_status")
    op.execute("DROP TYPE mockexamquestioncurationstatus")
    op.alter_column("mock_exam_questions", "created_by_admin_id", nullable=False)
