from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.courses.models import Course, CourseOffering
from nutrack.database import BaseRepository
from nutrack.enrollments.models import Enrollment
from nutrack.study.models import (
    MaterialCurationStatus,
    StudyMaterialLibraryEntry,
    StudyMaterialUpload,
)


def _offering_loader():
    return joinedload(CourseOffering.course).load_only(
        Course.code,
        Course.level,
        Course.title,
    )


def _upload_loader():
    return (
        joinedload(StudyMaterialUpload.course_offering)
        .options(_offering_loader())
    )


def _library_loader():
    return (
        joinedload(StudyMaterialLibraryEntry.upload)
        .joinedload(StudyMaterialUpload.course_offering)
        .options(_offering_loader())
    )


class StudyMaterialUploadRepository(BaseRepository[StudyMaterialUpload]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudyMaterialUpload)

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

    async def get_upload_by_id(
        self,
        upload_id: int,
    ) -> StudyMaterialUpload | None:
        stmt = self._base_query().where(StudyMaterialUpload.id == upload_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_uploads(
        self,
        user_id: int,
        course_id: int,
    ) -> list[StudyMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                StudyMaterialUpload.uploader_id == user_id,
                StudyMaterialUpload.course_id == course_id,
            )
            .order_by(StudyMaterialUpload.created_at.desc())
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
    ) -> list[StudyMaterialUpload]:
        stmt = self._base_query().options(joinedload(StudyMaterialUpload.uploader))
        if course_id is not None:
            stmt = stmt.where(StudyMaterialUpload.course_id == course_id)
        if user_id is not None:
            stmt = stmt.where(StudyMaterialUpload.uploader_id == user_id)
        if upload_status is not None:
            stmt = stmt.where(StudyMaterialUpload.upload_status == upload_status)
        stmt = stmt.where(StudyMaterialUpload.curation_status.in_(curation_statuses))
        stmt = stmt.order_by(StudyMaterialUpload.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_stale_uploads(
        self,
        cutoff: datetime,
        statuses: tuple,
    ) -> list[StudyMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                StudyMaterialUpload.upload_status.in_(statuses),
                StudyMaterialUpload.updated_at < cutoff,
            )
            .order_by(StudyMaterialUpload.updated_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    def _base_query(self) -> Select[tuple[StudyMaterialUpload]]:
        return select(StudyMaterialUpload).options(
            _upload_loader(),
            joinedload(StudyMaterialUpload.library_entry),
        )


class StudyMaterialLibraryRepository(BaseRepository[StudyMaterialLibraryEntry]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudyMaterialLibraryEntry)

    async def list_course_library(
        self,
        course_id: int,
    ) -> list[StudyMaterialLibraryEntry]:
        stmt = (
            select(StudyMaterialLibraryEntry)
            .options(_library_loader())
            .where(StudyMaterialLibraryEntry.course_id == course_id)
            .order_by(
                StudyMaterialLibraryEntry.curated_week.asc(),
                StudyMaterialLibraryEntry.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_upload_id(
        self,
        upload_id: int,
    ) -> StudyMaterialLibraryEntry | None:
        stmt = (
            select(StudyMaterialLibraryEntry)
            .options(_library_loader())
            .where(StudyMaterialLibraryEntry.upload_id == upload_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
