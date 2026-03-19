"""assessments fk to course_offerings

Revision ID: d7f3b9e1c042
Revises: c2d4f6e8a0b1
Create Date: 2026-03-19 13:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d7f3b9e1c042"
down_revision: Union[str, None] = "c2d4f6e8a0b1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_assessments_user_course", table_name="assessments")
    op.drop_constraint(
        "assessments_course_id_fkey", "assessments", type_="foreignkey"
    )
    op.create_foreign_key(
        "assessments_course_id_fkey",
        "assessments",
        "course_offerings",
        ["course_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_assessments_user_course", "assessments", ["user_id", "course_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_assessments_user_course", table_name="assessments")
    op.drop_constraint(
        "assessments_course_id_fkey", "assessments", type_="foreignkey"
    )
    op.create_foreign_key(
        "assessments_course_id_fkey",
        "assessments",
        "courses",
        ["course_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index(
        "ix_assessments_user_course", "assessments", ["user_id", "course_id"]
    )
