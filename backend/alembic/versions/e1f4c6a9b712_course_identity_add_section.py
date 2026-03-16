"""course identity add section

Revision ID: e1f4c6a9b712
Revises: 32d0a86858a2
Create Date: 2026-03-16 17:35:00.000000

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "e1f4c6a9b712"
down_revision: Union[str, None] = "32d0a86858a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_courses_code_level",
        "courses",
        type_="unique",
    )
    op.create_unique_constraint(
        "uq_courses_code_level_section",
        "courses",
        ["code", "level", "section"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_courses_code_level_section",
        "courses",
        type_="unique",
    )
    op.execute(
        """
        DELETE FROM courses c1
        USING courses c2
        WHERE c1.id > c2.id
          AND c1.code = c2.code
          AND c1.level = c2.level
        """
    )
    op.create_unique_constraint(
        "uq_courses_code_level",
        "courses",
        ["code", "level"],
    )
