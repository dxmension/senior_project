"""squashed — all migrations combined

Revision ID: 0001_squashed
Revises:
Create Date: 2026-04-18
"""

from typing import Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_squashed"
down_revision: Union[str, None] = None
branch_labels = None
depends_on = None

# ---------------------------------------------------------------------------
# Enum type objects (create_type=False — we call .create() manually)
# ---------------------------------------------------------------------------

assessment_type = postgresql.ENUM(
    "homework", "quiz", "midterm", "final", "project", "lab", "presentation", "other",
    name="assessment_type",
    create_type=False,
)
enrollment_status = postgresql.ENUM(
    "PASSED", "IN_PROGRESS", "WITHDRAWN", "FAILED", "AUDIT", "INCOMPLETE",
    name="enrollmentstatus",
    create_type=False,
)
recurrence_type = postgresql.ENUM(
    "none", "daily", "weekly", "biweekly", "monthly",
    name="recurrence_type",
    create_type=False,
)
material_upload_status = postgresql.ENUM(
    "QUEUED", "UPLOADING", "COMPLETED", "FAILED",
    name="materialuploadstatus",
    create_type=False,
)
# NOTE: includes NOT_REQUESTED added in the old migration 0003
material_curation_status = postgresql.ENUM(
    "PENDING", "PUBLISHED", "REJECTED", "NOT_REQUESTED",
    name="materialcurationstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    assessment_type.create(bind, checkfirst=True)
    enrollment_status.create(bind, checkfirst=True)
    recurrence_type.create(bind, checkfirst=True)
    material_upload_status.create(bind, checkfirst=True)
    material_curation_status.create(bind, checkfirst=True)

    # ------------------------------------------------------------------
    # courses
    # ------------------------------------------------------------------
    op.create_table(
        "courses",
        sa.Column("code", sa.String(16), nullable=False),
        sa.Column("level", sa.String(16), nullable=False),
        sa.Column("title", sa.String(256), nullable=False),
        sa.Column("department", sa.String(64), nullable=True),
        sa.Column("ects", sa.Integer(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("pass_grade", sa.String(), nullable=True),
        sa.Column("school", sa.String(32), nullable=True),
        sa.Column("academic_level", sa.String(16), nullable=True),
        sa.Column("credits_us", sa.Float(), nullable=True),
        sa.Column("prerequisites", sa.Text(), nullable=True),
        sa.Column("corequisites", sa.Text(), nullable=True),
        sa.Column("antirequisites", sa.Text(), nullable=True),
        sa.Column("priority_1", sa.Text(), nullable=True),
        sa.Column("priority_2", sa.Text(), nullable=True),
        sa.Column("priority_3", sa.Text(), nullable=True),
        sa.Column("priority_4", sa.Text(), nullable=True),
        sa.Column("requirements_term", sa.String(16), nullable=True),
        sa.Column("requirements_year", sa.Integer(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code", "level", name="uq_courses_code_level"),
    )
    op.create_index(op.f("ix_courses_id"), "courses", ["id"], unique=True)

    # ------------------------------------------------------------------
    # users  (includes kazakh_level from old migration 0004)
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("google_id", sa.String(255), nullable=False),
        sa.Column("first_name", sa.String(64), nullable=False),
        sa.Column("last_name", sa.String(64), nullable=False),
        sa.Column("major", sa.String(64), nullable=True),
        sa.Column("kazakh_level", sa.String(8), nullable=True),
        sa.Column("study_year", sa.Integer(), nullable=True),
        sa.Column("cgpa", sa.Float(), nullable=True),
        sa.Column("total_credits_earned", sa.Integer(), nullable=True),
        sa.Column("total_credits_enrolled", sa.Integer(), nullable=True),
        sa.Column("avatar_url", sa.String(), nullable=True),
        sa.Column("is_onboarded", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=True)

    # ------------------------------------------------------------------
    # categories
    # ------------------------------------------------------------------
    op.create_table(
        "categories",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("color", sa.String(7), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "name", name="uq_categories_user_name"),
    )
    op.create_index(op.f("ix_categories_id"), "categories", ["id"], unique=True)
    op.create_index("ix_categories_user_id", "categories", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # course_offerings
    # ------------------------------------------------------------------
    op.create_table(
        "course_offerings",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(16), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("days", sa.String(64), nullable=True),
        sa.Column("meeting_time", sa.String(64), nullable=True),
        sa.Column("enrolled", sa.Integer(), nullable=True),
        sa.Column("capacity", sa.Integer(), nullable=True),
        sa.Column("faculty", sa.Text(), nullable=True),
        sa.Column("room", sa.String(128), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id", "term", "year", "section",
            name="uq_course_offerings_course_term_year_section",
        ),
    )
    op.create_index(op.f("ix_course_offerings_id"), "course_offerings", ["id"], unique=True)

    # ------------------------------------------------------------------
    # course_gpa_stats
    # ------------------------------------------------------------------
    op.create_table(
        "course_gpa_stats",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("section", sa.String(16), nullable=True),
        sa.Column("avg_gpa", sa.Float(), nullable=True),
        sa.Column("total_enrolled", sa.Integer(), nullable=True),
        sa.Column("grade_distribution", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "course_id", "term", "year", "section",
            name="uq_course_gpa_stats_course_term_year_section",
        ),
    )
    op.create_index(op.f("ix_course_gpa_stats_id"), "course_gpa_stats", ["id"], unique=True)

    # ------------------------------------------------------------------
    # course_reviews
    # ------------------------------------------------------------------
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
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("difficulty IS NULL OR difficulty BETWEEN 1 AND 5", name="ck_review_difficulty"),
        sa.CheckConstraint("gpa_boost IS NULL OR gpa_boost BETWEEN 1 AND 5", name="ck_review_gpa_boost"),
        sa.CheckConstraint("informativeness IS NULL OR informativeness BETWEEN 1 AND 5", name="ck_review_informativeness"),
        sa.CheckConstraint("overall_rating BETWEEN 1 AND 5", name="ck_review_overall_rating"),
        sa.CheckConstraint("workload IS NULL OR workload BETWEEN 1 AND 5", name="ck_review_workload"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "user_id", name="uq_course_reviews_course_user"),
    )
    op.create_index(op.f("ix_course_reviews_course_id"), "course_reviews", ["course_id"], unique=False)
    op.create_index(op.f("ix_course_reviews_id"), "course_reviews", ["id"], unique=True)
    op.create_index(op.f("ix_course_reviews_user_id"), "course_reviews", ["user_id"], unique=False)

    # ------------------------------------------------------------------
    # assessments
    # ------------------------------------------------------------------
    op.create_table(
        "assessments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("assessment_type", assessment_type, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=False),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("max_score", sa.Float(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_assessments_id"), "assessments", ["id"], unique=True)
    op.create_index("ix_assessments_user_course", "assessments", ["user_id", "course_id"], unique=False)
    op.create_index("ix_assessments_user_deadline", "assessments", ["user_id", "deadline"], unique=False)

    # ------------------------------------------------------------------
    # enrollments
    # ------------------------------------------------------------------
    op.create_table(
        "enrollments",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("term", sa.String(16), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("grade", sa.String(4), nullable=True),
        sa.Column("grade_points", sa.Float(), nullable=True),
        sa.Column("status", enrollment_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "course_id", "term", "year"),
    )

    # ------------------------------------------------------------------
    # events
    # ------------------------------------------------------------------
    op.create_table(
        "events",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("start_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_all_day", sa.Boolean(), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("recurrence", recurrence_type, nullable=False),
        sa.Column("recurrence_end_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_events_id"), "events", ["id"], unique=True)
    op.create_index("ix_events_user_category", "events", ["user_id", "category_id"], unique=False)
    op.create_index("ix_events_user_start_at", "events", ["user_id", "start_at"], unique=False)

    # ------------------------------------------------------------------
    # study_material_uploads
    # ------------------------------------------------------------------
    op.create_table(
        "study_material_uploads",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("uploader_id", sa.Integer(), nullable=False),
        sa.Column("user_week", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("staged_path", sa.String(512), nullable=True),
        sa.Column("storage_key", sa.String(512), nullable=False),
        sa.Column("content_type", sa.String(128), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("upload_status", material_upload_status, nullable=False),
        sa.Column("curation_status", material_curation_status, nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploader_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_study_material_uploads_course_id", "study_material_uploads", ["course_id"], unique=False)
    op.create_index("ix_study_material_uploads_uploader_id", "study_material_uploads", ["uploader_id"], unique=False)
    op.create_index("ix_study_material_uploads_status_created", "study_material_uploads", ["upload_status", "created_at"], unique=False)
    op.create_index("ix_study_material_uploads_user_course_created", "study_material_uploads", ["uploader_id", "course_id", "created_at"], unique=False)

    # ------------------------------------------------------------------
    # study_material_library_entries
    # ------------------------------------------------------------------
    op.create_table(
        "study_material_library_entries",
        sa.Column("upload_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("curated_title", sa.String(255), nullable=False),
        sa.Column("curated_week", sa.Integer(), nullable=False),
        sa.Column("curated_by_admin_id", sa.Integer(), nullable=False),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["curated_by_admin_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["upload_id"], ["study_material_uploads.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("upload_id", name="uq_study_material_library_upload"),
    )
    op.create_index(
        "ix_study_material_library_entries_course_week_created",
        "study_material_library_entries",
        ["course_id", "curated_week", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_study_material_library_entries_course_week_created", table_name="study_material_library_entries")
    op.drop_table("study_material_library_entries")

    op.drop_index("ix_study_material_uploads_user_course_created", table_name="study_material_uploads")
    op.drop_index("ix_study_material_uploads_status_created", table_name="study_material_uploads")
    op.drop_index("ix_study_material_uploads_uploader_id", table_name="study_material_uploads")
    op.drop_index("ix_study_material_uploads_course_id", table_name="study_material_uploads")
    op.drop_table("study_material_uploads")

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

    material_curation_status.drop(op.get_bind(), checkfirst=True)
    material_upload_status.drop(op.get_bind(), checkfirst=True)
    recurrence_type.drop(op.get_bind(), checkfirst=True)
    enrollment_status.drop(op.get_bind(), checkfirst=True)
    assessment_type.drop(op.get_bind(), checkfirst=True)
