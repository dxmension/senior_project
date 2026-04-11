"""initial

Revision ID: 20260411_0001
Revises:
Create Date: 2026-04-11 16:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "20260411_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

assessment_type = postgresql.ENUM(
    "homework",
    "quiz",
    "midterm",
    "final",
    "project",
    "lab",
    "presentation",
    "other",
    name="assessment_type",
    create_type=False,
)
enrollment_status = postgresql.ENUM(
    "PASSED",
    "IN_PROGRESS",
    "WITHDRAWN",
    "FAILED",
    "AUDIT",
    "INCOMPLETE",
    name="enrollmentstatus",
    create_type=False,
)
recurrence_type = postgresql.ENUM(
    "none",
    "daily",
    "weekly",
    "biweekly",
    "monthly",
    name="recurrence_type",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    assessment_type.create(bind, checkfirst=True)
    enrollment_status.create(bind, checkfirst=True)
    recurrence_type.create(bind, checkfirst=True)

    op.create_table(
        "courses",
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("level", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("department", sa.String(length=64), nullable=True),
        sa.Column("ects", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("pass_grade", sa.String(), nullable=True),
        sa.Column("school", sa.String(length=32), nullable=True),
        sa.Column("academic_level", sa.String(length=16), nullable=True),
        sa.Column("credits_us", sa.Float(), nullable=True),
        sa.Column("prerequisites", sa.Text(), nullable=True),
        sa.Column("corequisites", sa.Text(), nullable=True),
        sa.Column("antirequisites", sa.Text(), nullable=True),
        sa.Column("priority_1", sa.Text(), nullable=True),
        sa.Column("priority_2", sa.Text(), nullable=True),
        sa.Column("priority_3", sa.Text(), nullable=True),
        sa.Column("priority_4", sa.Text(), nullable=True),
        sa.Column("requirements_term", sa.String(length=16), nullable=True),
        sa.Column("requirements_year", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", "level", name="uq_courses_code_level"),
    )
    op.create_index(op.f("ix_courses_id"), "courses", ["id"], unique=True)

    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=64), nullable=False),
        sa.Column("last_name", sa.String(length=64), nullable=False),
        sa.Column("major", sa.String(length=64), nullable=True),
        sa.Column("study_year", sa.Integer(), nullable=True),
        sa.Column("cgpa", sa.Float(), nullable=True),
        sa.Column("total_credits_earned", sa.Integer(), nullable=True),
        sa.Column("total_credits_enrolled", sa.Integer(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("is_onboarded", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=True)

    op.create_table(
        "categories",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("color", sa.String(length=7), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=True)
    op.create_index("ix_categories_user_id", "categories", ["user_id"], unique=False)

    op.create_table(
        "course_offerings",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=16), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("days", sa.String(length=64), nullable=True),
        sa.Column("meeting_time", sa.String(length=64), nullable=True),
        sa.Column("enrolled", sa.Integer(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("faculty", sa.Text(), nullable=True),
        sa.Column("room", sa.String(length=128), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "term",
            "year",
            "section",
            name="uq_course_offerings_course_term_year_section",
        ),
    )
    op.create_index(
        op.f("ix_course_offerings_id"),
        "course_offerings",
        ["id"],
        unique=True,
    )

    op.create_table(
        "course_gpa_stats",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(length=16), nullable=True),
        sa.Column("avg_gpa", sa.Float(), nullable=True),
        sa.Column("total_enrolled", sa.Integer(), nullable=True),
        sa.Column("grade_distribution", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "term",
            "year",
            "section",
            name="uq_course_gpa_stats_course_term_year_section",
        ),
    )
    op.create_index(
        op.f("ix_course_gpa_stats_id"),
        "course_gpa_stats",
        ["id"],
        unique=True,
    )

    op.create_table(
        "course_reviews",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("overall_rating", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=True),
        sa.Column("informativeness", sa.Integer(), nullable=True),
        sa.Column("gpa_boost", sa.Integer(), nullable=True),
        sa.Column("workload", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.CheckConstraint(
            "difficulty IS NULL OR difficulty BETWEEN 1 AND 5",
            name="ck_review_difficulty",
        ),
        sa.CheckConstraint(
            "gpa_boost IS NULL OR gpa_boost BETWEEN 1 AND 5",
            name="ck_review_gpa_boost",
        ),
        sa.CheckConstraint(
            "informativeness IS NULL OR informativeness BETWEEN 1 AND 5",
            name="ck_review_informativeness",
        ),
        sa.CheckConstraint(
            "overall_rating BETWEEN 1 AND 5",
            name="ck_review_overall_rating",
        ),
        sa.CheckConstraint(
            "workload IS NULL OR workload BETWEEN 1 AND 5",
            name="ck_review_workload",
        ),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id",
            "user_id",
            name="uq_course_reviews_course_user",
        ),
    )
    op.create_index(
        op.f("ix_course_reviews_course_id"),
        "course_reviews",
        ["course_id"],
        unique=False,
    )
    op.create_index(op.f("ix_course_reviews_id"), "course_reviews", ["id"], unique=True)
    op.create_index(
        op.f("ix_course_reviews_user_id"),
        "course_reviews",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "assessments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column(
            "assessment_type",
            assessment_type,
            nullable=False,
        ),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["course_offerings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessments_id"), "assessments", ["id"], unique=True)
    op.create_index(
        "ix_assessments_user_course",
        "assessments",
        ["user_id", "course_id"],
        unique=False,
    )
    op.create_index(
        "ix_assessments_user_deadline",
        "assessments",
        ["user_id", "deadline"],
        unique=False,
    )

    op.create_table(
        "enrollments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(length=16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("grade", sa.String(length=4), nullable=True),
        sa.Column("grade_points", sa.Float(), nullable=True),
        sa.Column("status", enrollment_status, nullable=False),
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
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["course_offerings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "course_id", "term", "year"),
    )

    op.create_table(
        "events",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_all_day", sa.Boolean(), nullable=False),
        sa.Column("location", sa.String(length=255), nullable=True),
        sa.Column("recurrence", recurrence_type, nullable=False),
        sa.Column("recurrence_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=True)
    op.create_index(
        "ix_events_user_category",
        "events",
        ["user_id", "category_id"],
        unique=False,
    )
    op.create_index(
        "ix_events_user_start_at",
        "events",
        ["user_id", "start_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_events_user_start_at", table_name="events")
    op.drop_index("ix_events_user_category", table_name="events")
    op.drop_index(op.f("ix_events_id"), table_name="events")
    op.drop_table("events")

    op.drop_table("enrollments")

    op.drop_index("ix_assessments_user_deadline", table_name="assessments")
    op.drop_index("ix_assessments_user_course", table_name="assessments")
    op.drop_index(op.f("ix_assessments_id"), table_name="assessments")
    op.drop_table("assessments")

    op.drop_index(op.f("ix_course_reviews_user_id"), table_name="course_reviews")
    op.drop_index(op.f("ix_course_reviews_id"), table_name="course_reviews")
    op.drop_index(op.f("ix_course_reviews_course_id"), table_name="course_reviews")
    op.drop_table("course_reviews")

    op.drop_index(op.f("ix_course_gpa_stats_id"), table_name="course_gpa_stats")
    op.drop_table("course_gpa_stats")

    op.drop_index(op.f("ix_course_offerings_id"), table_name="course_offerings")
    op.drop_table("course_offerings")

    op.drop_index("ix_categories_user_id", table_name="categories")
    op.drop_index(op.f("ix_categories_id"), table_name="categories")
    op.drop_table("categories")

    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")

    op.drop_index(op.f("ix_courses_id"), table_name="courses")
    op.drop_table("courses")

    recurrence_type.drop(op.get_bind(), checkfirst=True)
    enrollment_status.drop(op.get_bind(), checkfirst=True)
    assessment_type.drop(op.get_bind(), checkfirst=True)
