"""add course_reviews table

Revision ID: b2c3d4e5f6a1
Revises: f1a2b3c4d5e6
Create Date: 2026-03-25

Adds:
  - course_reviews table with per-user, per-course review records
    Fields: overall_rating (1-5, required), comment (text, optional),
    difficulty / informativeness / gpa_boost / workload (1-5, optional),
    created_at / updated_at timestamps.
  - Unique constraint: one review per (course_id, user_id).
  - Check constraints on all rating columns.
"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision: str = "b2c3d4e5f6a1"
down_revision: str | None = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "course_reviews",
        sa.Column("id", sa.Integer(), primary_key=True, index=True, unique=True, nullable=False),
        sa.Column(
            "course_id",
            sa.Integer(),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("overall_rating", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("informativeness", sa.Integer(), nullable=True),
        sa.Column("gpa_boost", sa.Integer(), nullable=True),
        sa.Column("workload", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("course_id", "user_id", name="uq_course_reviews_course_user"),
        sa.CheckConstraint("overall_rating BETWEEN 1 AND 5", name="ck_review_overall_rating"),
        sa.CheckConstraint("difficulty IS NULL OR difficulty BETWEEN 1 AND 5", name="ck_review_difficulty"),
        sa.CheckConstraint("informativeness IS NULL OR informativeness BETWEEN 1 AND 5", name="ck_review_informativeness"),
        sa.CheckConstraint("gpa_boost IS NULL OR gpa_boost BETWEEN 1 AND 5", name="ck_review_gpa_boost"),
        sa.CheckConstraint("workload IS NULL OR workload BETWEEN 1 AND 5", name="ck_review_workload"),
    )


def downgrade() -> None:
    op.drop_table("course_reviews")
