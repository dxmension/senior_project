"""flashcard domain

Revision ID: 20260420_0013
Revises: 20260419_0012
Create Date: 2026-04-20 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260420_0013"
down_revision: Union[str, None] = "20260419_0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "flashcard_decks",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("course_offerings.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("card_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("difficulty", sa.String(16), nullable=False),
        sa.Column(
            "owner_user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_flashcard_decks_id", "flashcard_decks", ["id"], unique=True)
    op.create_index("ix_flashcard_decks_course_id", "flashcard_decks", ["course_id"])
    op.create_index("ix_flashcard_decks_owner_user_id", "flashcard_decks", ["owner_user_id"])

    op.create_table(
        "flashcards",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "deck_id",
            sa.Integer(),
            sa.ForeignKey("flashcard_decks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("topic", sa.String(128), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("deck_id", "position", name="uq_flashcards_deck_position"),
    )
    op.create_index("ix_flashcards_id", "flashcards", ["id"], unique=True)
    op.create_index("ix_flashcards_deck_id", "flashcards", ["deck_id"])

    op.create_table(
        "flashcard_sessions",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "deck_id",
            sa.Integer(),
            sa.ForeignKey("flashcard_decks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ai_review", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_flashcard_sessions_id", "flashcard_sessions", ["id"], unique=True)
    op.create_index("ix_flashcard_sessions_deck_id", "flashcard_sessions", ["deck_id"])
    op.create_index("ix_flashcard_sessions_user_id", "flashcard_sessions", ["user_id"])

    op.create_table(
        "flashcard_session_cards",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column(
            "session_id",
            sa.Integer(),
            sa.ForeignKey("flashcard_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "flashcard_id",
            sa.Integer(),
            sa.ForeignKey("flashcards.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("times_seen", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("times_easy", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("times_medium", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("times_hard", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_response", sa.String(16), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("session_id", "flashcard_id", name="uq_flashcard_session_cards"),
    )
    op.create_index(
        "ix_flashcard_session_cards_id", "flashcard_session_cards", ["id"], unique=True
    )
    op.create_index(
        "ix_flashcard_session_cards_session_id",
        "flashcard_session_cards",
        ["session_id"],
    )


def downgrade() -> None:
    op.drop_table("flashcard_session_cards")
    op.drop_table("flashcard_sessions")
    op.drop_table("flashcards")
    op.drop_table("flashcard_decks")
