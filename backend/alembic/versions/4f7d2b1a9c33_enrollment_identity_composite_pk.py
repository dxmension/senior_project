"""enrollment identity composite pk

Revision ID: 4f7d2b1a9c33
Revises: e1f4c6a9b712
Create Date: 2026-03-16 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision: str = "4f7d2b1a9c33"
down_revision: Union[str, None] = "e1f4c6a9b712"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index(op.f("ix_enrollments_id"), table_name="enrollments")
    op.drop_constraint("uq_enrollment", "enrollments", type_="unique")
    op.drop_constraint("enrollments_pkey", "enrollments", type_="primary")
    op.drop_column("enrollments", "id")
    op.create_primary_key(
        "pk_enrollments",
        "enrollments",
        ["user_id", "course_id", "semester"],
    )


def downgrade() -> None:
    op.drop_constraint("pk_enrollments", "enrollments", type_="primary")
    op.add_column(
        "enrollments",
        sa.Column("id", sa.Integer(), nullable=True),
    )
    op.execute(
        sa.text(
            """
            CREATE SEQUENCE IF NOT EXISTS enrollments_id_seq
            OWNED BY enrollments.id
            """
        )
    )
    op.execute(
        sa.text(
            """
            ALTER TABLE enrollments
            ALTER COLUMN id SET DEFAULT nextval('enrollments_id_seq')
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE enrollments
            SET id = nextval('enrollments_id_seq')
            WHERE id IS NULL
            """
        )
    )
    op.alter_column("enrollments", "id", nullable=False)
    op.create_primary_key("enrollments_pkey", "enrollments", ["id"])
    op.create_unique_constraint(
        "uq_enrollment",
        "enrollments",
        ["user_id", "course_id", "semester"],
    )
    op.create_index(op.f("ix_enrollments_id"), "enrollments", ["id"], unique=True)
