import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from nutrack.models import Base, IDMixin, TimestampMixin

if TYPE_CHECKING:
    from nutrack.courses.models import CourseOffering
    from nutrack.users.models import User


class MaterialUploadStatus(str, enum.Enum):
    QUEUED = "queued"
    UPLOADING = "uploading"
    COMPLETED = "completed"
    FAILED = "failed"


class MaterialCurationStatus(str, enum.Enum):
    NOT_REQUESTED = "not_requested"
    PENDING = "pending"
    PUBLISHED = "published"
    REJECTED = "rejected"


class CourseMaterialUpload(Base, IDMixin, TimestampMixin):
    __tablename__ = "study_material_uploads"

    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    uploader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_week: Mapped[int] = mapped_column(Integer, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    staged_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    storage_key: Mapped[str] = mapped_column(String(512), nullable=False)
    content_type: Mapped[str] = mapped_column(String(128), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    upload_status: Mapped[MaterialUploadStatus] = mapped_column(
        Enum(MaterialUploadStatus),
        nullable=False,
        default=MaterialUploadStatus.QUEUED,
    )
    curation_status: Mapped[MaterialCurationStatus] = mapped_column(
        Enum(MaterialCurationStatus),
        nullable=False,
        default=MaterialCurationStatus.PENDING,
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    course_offering: Mapped["CourseOffering"] = relationship()
    uploader: Mapped["User"] = relationship()
    library_entry: Mapped["CourseMaterialLibraryEntry | None"] = relationship(
        back_populates="upload",
        uselist=False,
    )


class CourseMaterialLibraryEntry(Base, IDMixin, TimestampMixin):
    __tablename__ = "study_material_library_entries"
    __table_args__ = (
        UniqueConstraint("upload_id", name="uq_study_material_library_upload"),
    )

    upload_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("study_material_uploads.id", ondelete="CASCADE"),
        nullable=False,
    )
    course_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("course_offerings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    curated_title: Mapped[str] = mapped_column(String(255), nullable=False)
    curated_week: Mapped[int] = mapped_column(Integer, nullable=False)
    curated_by_admin_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    upload: Mapped[CourseMaterialUpload] = relationship(
        back_populates="library_entry"
    )
    course_offering: Mapped["CourseOffering"] = relationship()
    curated_by_admin: Mapped["User"] = relationship()
