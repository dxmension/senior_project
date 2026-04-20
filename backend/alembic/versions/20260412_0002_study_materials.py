"""study materials

Revision ID: 20260412_0002
Revises: 20260411_0001
Create Date: 2026-04-12 11:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260412_0002"
down_revision: Union[str, None] = "20260411_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

material_upload_status = postgresql.ENUM(
    "QUEUED",
    "UPLOADING",
    "COMPLETED",
    "FAILED",
    name="materialuploadstatus",
    create_type=False,
)
material_curation_status = postgresql.ENUM(
    "PENDING",
    "PUBLISHED",
    "REJECTED",
    name="materialcurationstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    material_upload_status.create(bind, checkfirst=True)
    material_curation_status.create(bind, checkfirst=True)

    existing = set(sa.inspect(bind).get_table_names())

    if "study_material_uploads" not in existing:
        op.create_table(
        "study_material_uploads",
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("uploader_id", sa.Integer(), nullable=False),
        sa.Column("user_week", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("staged_path", sa.String(length=512), nullable=True),
        sa.Column("storage_key", sa.String(length=512), nullable=False),
        sa.Column("content_type", sa.String(length=128), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("upload_status", material_upload_status, nullable=False),
        sa.Column("curation_status", material_curation_status, nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploader_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_study_material_uploads_course_id",
            "study_material_uploads",
            ["course_id"],
            unique=False,
        )
        op.create_index(
            "ix_study_material_uploads_uploader_id",
            "study_material_uploads",
            ["uploader_id"],
            unique=False,
        )
        op.create_index(
            "ix_study_material_uploads_status_created",
            "study_material_uploads",
            ["upload_status", "created_at"],
            unique=False,
        )
        op.create_index(
            "ix_study_material_uploads_user_course_created",
            "study_material_uploads",
            ["uploader_id", "course_id", "created_at"],
            unique=False,
        )

    if "study_material_library_entries" not in existing:
        op.create_table(
        "study_material_library_entries",
        sa.Column("upload_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("curated_title", sa.String(length=255), nullable=False),
        sa.Column("curated_week", sa.Integer(), nullable=False),
        sa.Column("curated_by_admin_id", sa.Integer(), nullable=False),
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
        sa.ForeignKeyConstraint(["course_id"], ["course_offerings.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["curated_by_admin_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["upload_id"],
            ["study_material_uploads.id"],
            ondelete="CASCADE",
        ),
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
    op.drop_index(
        "ix_study_material_library_entries_course_week_created",
        table_name="study_material_library_entries",
    )
    op.drop_table("study_material_library_entries")

    op.drop_index(
        "ix_study_material_uploads_user_course_created",
        table_name="study_material_uploads",
    )
    op.drop_index(
        "ix_study_material_uploads_status_created",
        table_name="study_material_uploads",
    )
    op.drop_index(
        "ix_study_material_uploads_uploader_id",
        table_name="study_material_uploads",
    )
    op.drop_index(
        "ix_study_material_uploads_course_id",
        table_name="study_material_uploads",
    )
    op.drop_table("study_material_uploads")

    material_curation_status.drop(op.get_bind(), checkfirst=True)
    material_upload_status.drop(op.get_bind(), checkfirst=True)
