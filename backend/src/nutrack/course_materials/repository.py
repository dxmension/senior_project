from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.course_materials.models import (
    CourseMaterialLibraryEntry,
    CourseMaterialUpload,
    MaterialCurationStatus,
    MaterialUploadStatus,
)
from nutrack.courses.models import Course, CourseOffering
from nutrack.database import BaseRepository
from nutrack.enrollments.models import Enrollment


def _offering_loader():
    return joinedload(CourseOffering.course).load_only(
        Course.code,
        Course.level,
        Course.title,
    )


def _upload_loader():
    return joinedload(CourseMaterialUpload.course_offering).options(
        _offering_loader()
    )


def _library_loader():
    return (
        joinedload(CourseMaterialLibraryEntry.upload)
        .joinedload(CourseMaterialUpload.course_offering)
        .options(_offering_loader())
    )


class CourseMaterialUploadRepository(BaseRepository[CourseMaterialUpload]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CourseMaterialUpload)

    async def get_enrolled_course(
        self,
        user_id: int,
        course_id: int,
    ) -> CourseOffering | None:
        stmt = (
            select(CourseOffering)
            .join(Enrollment, Enrollment.course_id == CourseOffering.id)
            .options(_offering_loader())
            .where(
                Enrollment.user_id == user_id,
                CourseOffering.id == course_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_upload_by_id(self, upload_id: int) -> CourseMaterialUpload | None:
        stmt = self._base_query().where(CourseMaterialUpload.id == upload_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_completed_uploads_for_week(
        self,
        user_id: int,
        course_id: int,
        week: int,
    ) -> list[CourseMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                CourseMaterialUpload.uploader_id == user_id,
                CourseMaterialUpload.course_id == course_id,
                CourseMaterialUpload.user_week == week,
                CourseMaterialUpload.upload_status == MaterialUploadStatus.COMPLETED,
            )
            .order_by(CourseMaterialUpload.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_user_uploads(
        self,
        user_id: int,
        course_id: int,
    ) -> list[CourseMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                CourseMaterialUpload.uploader_id == user_id,
                CourseMaterialUpload.course_id == course_id,
            )
            .order_by(CourseMaterialUpload.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_admin_uploads(
        self,
        *,
        course_id: int | None = None,
        user_id: int | None = None,
        upload_status: str | None = None,
        curation_statuses: tuple[MaterialCurationStatus, ...],
    ) -> list[CourseMaterialUpload]:
        stmt = self._base_query().options(joinedload(CourseMaterialUpload.uploader))
        if course_id is not None:
            stmt = stmt.where(CourseMaterialUpload.course_id == course_id)
        if user_id is not None:
            stmt = stmt.where(CourseMaterialUpload.uploader_id == user_id)
        if upload_status is not None:
            stmt = stmt.where(CourseMaterialUpload.upload_status == upload_status)
        stmt = stmt.where(CourseMaterialUpload.curation_status.in_(curation_statuses))
        stmt = stmt.order_by(CourseMaterialUpload.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_stale_uploads(
        self,
        cutoff: datetime,
        statuses: tuple,
    ) -> list[CourseMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                CourseMaterialUpload.upload_status.in_(statuses),
                CourseMaterialUpload.updated_at < cutoff,
            )
            .order_by(CourseMaterialUpload.updated_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    def _base_query(self) -> Select[tuple[CourseMaterialUpload]]:
        return select(CourseMaterialUpload).options(
            _upload_loader(),
            joinedload(CourseMaterialUpload.library_entry),
        )


class CourseMaterialLibraryRepository(
    BaseRepository[CourseMaterialLibraryEntry]
):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, CourseMaterialLibraryEntry)

    async def list_course_library(
        self,
        course_id: int,
    ) -> list[CourseMaterialLibraryEntry]:
        stmt = (
            select(CourseMaterialLibraryEntry)
            .options(_library_loader())
            .where(CourseMaterialLibraryEntry.course_id == course_id)
            .order_by(
                CourseMaterialLibraryEntry.curated_week.asc(),
                CourseMaterialLibraryEntry.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_upload_id(
        self,
        upload_id: int,
    ) -> CourseMaterialLibraryEntry | None:
        stmt = (
            select(CourseMaterialLibraryEntry)
            .options(_library_loader())
            .where(CourseMaterialLibraryEntry.upload_id == upload_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
