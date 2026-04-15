import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.config import settings
from nutrack.storage import ObjectStorage, sanitize_filename, slugify
from nutrack.study.exceptions import (
    StudyMaterialForbiddenError,
    StudyMaterialNotFoundError,
    StudyMaterialQueueError,
    StudyMaterialValidationError,
)
from nutrack.study.models import (
    MaterialCurationStatus,
    MaterialUploadStatus,
    StudyMaterialLibraryEntry,
    StudyMaterialUpload,
)
from nutrack.study.repository import (
    StudyMaterialLibraryRepository,
    StudyMaterialUploadRepository,
)

MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_FILES_PER_BATCH = 10
STALE_UPLOAD_MINUTES = 15
ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


def format_course_code(code: str, level: str) -> str:
    return f"{code} {level}".strip() if level and level != "0" else code


def _publish_requested(status: MaterialCurationStatus) -> bool:
    return status != MaterialCurationStatus.NOT_REQUESTED


def _admin_visible_curation_statuses(
    curation_status: MaterialCurationStatus | None,
) -> tuple[MaterialCurationStatus, ...]:
    visible_statuses = (
        MaterialCurationStatus.PENDING,
        MaterialCurationStatus.PUBLISHED,
    )
    if curation_status is None:
        return visible_statuses
    if curation_status in visible_statuses:
        return (curation_status,)
    return ()


def _upload_response(
    upload: StudyMaterialUpload,
    download_url: str | None,
):
    course = upload.course_offering.course
    return {
        "id": upload.id,
        "course_id": upload.course_id,
        "course_code": format_course_code(course.code, course.level),
        "course_title": course.title,
        "week": upload.user_week,
        "original_filename": upload.original_filename,
        "content_type": upload.content_type,
        "file_size_bytes": upload.file_size_bytes,
        "upload_status": upload.upload_status.value,
        "curation_status": upload.curation_status.value,
        "publish_requested": _publish_requested(upload.curation_status),
        "error_message": upload.error_message,
        "is_published": upload.library_entry is not None,
        "download_url": download_url,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }


def _library_response(
    entry: StudyMaterialLibraryEntry,
    download_url: str | None,
    current_user_id: int,
):
    upload = entry.upload
    course = upload.course_offering.course
    return {
        "id": entry.id,
        "upload_id": upload.id,
        "course_id": entry.course_id,
        "course_code": format_course_code(course.code, course.level),
        "course_title": course.title,
        "week": entry.curated_week,
        "title": entry.curated_title,
        "original_filename": upload.original_filename,
        "content_type": upload.content_type,
        "file_size_bytes": upload.file_size_bytes,
        "download_url": download_url,
        "is_owned_by_current_user": upload.uploader_id == current_user_id,
        "published_at": entry.updated_at,
    }


def _admin_upload_response(
    upload: StudyMaterialUpload,
    download_url: str | None,
):
    course = upload.course_offering.course
    uploader = upload.uploader
    library_entry = upload.library_entry
    return {
        "id": upload.id,
        "course_id": upload.course_id,
        "course_code": format_course_code(course.code, course.level),
        "course_title": course.title,
        "uploader_id": uploader.id,
        "uploader_name": f"{uploader.first_name} {uploader.last_name}",
        "uploader_email": uploader.email,
        "user_week": upload.user_week,
        "shared_week": library_entry.curated_week if library_entry else None,
        "shared_title": library_entry.curated_title if library_entry else None,
        "original_filename": upload.original_filename,
        "content_type": upload.content_type,
        "file_size_bytes": upload.file_size_bytes,
        "upload_status": upload.upload_status.value,
        "curation_status": upload.curation_status.value,
        "error_message": upload.error_message,
        "download_url": download_url,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }


class StudyService:
    def __init__(
        self,
        session: AsyncSession,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.session = session
        self.upload_repo = StudyMaterialUploadRepository(session)
        self.library_repo = StudyMaterialLibraryRepository(session)
        self.storage = storage or ObjectStorage()

    async def queue_uploads(
        self,
        user_id: int,
        course_id: int,
        week: int,
        request_shared_library: bool,
        files: list[UploadFile],
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        offering = await self.upload_repo.get_enrolled_course(user_id, course_id)
        if not offering:
            raise StudyMaterialForbiddenError()
        self._validate_batch(week, files)
        uploads = []
        for file in files:
            uploads.append(
                await self._create_upload(
                    user_id,
                    offering,
                    week,
                    request_shared_library,
                    file,
                )
            )
        await self.session.commit()
        try:
            self._enqueue_uploads(uploads)
        except StudyMaterialQueueError:
            await self._mark_queue_failure(uploads)
            raise
        refreshed = [await self.upload_repo.get_upload_by_id(item.id) for item in uploads]
        return await self._serialize_uploads(refreshed)

    async def list_user_uploads(
        self,
        user_id: int,
        course_id: int,
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        await self._require_course_access(user_id, course_id)
        uploads = await self.upload_repo.list_user_uploads(user_id, course_id)
        return await self._serialize_uploads(uploads)

    async def list_shared_library(
        self,
        user_id: int,
        course_id: int,
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        await self._require_course_access(user_id, course_id)
        entries = await self.library_repo.list_course_library(course_id)
        return await self._serialize_library(entries, user_id)

    async def list_admin_uploads(
        self,
        *,
        course_id: int | None = None,
        user_id: int | None = None,
        upload_status: str | None = None,
        curation_status: MaterialCurationStatus | None = None,
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        curation_statuses = _admin_visible_curation_statuses(curation_status)
        if not curation_statuses:
            return []
        uploads = await self.upload_repo.list_admin_uploads(
            course_id=course_id,
            user_id=user_id,
            upload_status=upload_status,
            curation_statuses=curation_statuses,
        )
        payload = []
        for upload in uploads:
            url = await self._download_url(upload.storage_key, upload.upload_status)
            payload.append(_admin_upload_response(upload, url))
        return payload

    async def publish_upload(
        self,
        admin_id: int,
        upload_id: int,
        title: str,
        week: int,
    ) -> dict:
        await self._cleanup_stale_uploads()
        self._validate_week(week)
        if not title.strip():
            raise StudyMaterialValidationError("Title is required")
        upload = await self._load_upload(upload_id)
        if upload.upload_status != MaterialUploadStatus.COMPLETED:
            raise StudyMaterialValidationError("Only completed uploads can be published")
        if not _publish_requested(upload.curation_status):
            raise StudyMaterialValidationError(
                "This upload was not submitted for shared library curation"
            )
        library_entry = await self.library_repo.get_by_upload_id(upload.id)
        if library_entry:
            await self.library_repo.update(
                library_entry,
                curated_title=title.strip(),
                curated_week=week,
                curated_by_admin_id=admin_id,
            )
        else:
            library_entry = await self.library_repo.create(
                upload_id=upload.id,
                course_id=upload.course_id,
                curated_title=title.strip(),
                curated_week=week,
                curated_by_admin_id=admin_id,
            )
        await self.upload_repo.update(
            upload,
            curation_status=MaterialCurationStatus.PUBLISHED,
        )
        await self.session.commit()
        loaded = await self.library_repo.get_by_upload_id(upload.id)
        return _library_response(
            loaded,
            await self.storage.generate_download_url(upload.storage_key),
            upload.uploader_id,
        )

    async def reject_upload(self, upload_id: int) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_upload(upload_id)
        if upload.library_entry is not None:
            raise StudyMaterialValidationError("Published uploads cannot be rejected")
        if not _publish_requested(upload.curation_status):
            raise StudyMaterialValidationError("Private uploads cannot be rejected")
        await self.upload_repo.update(
            upload,
            curation_status=MaterialCurationStatus.REJECTED,
        )
        await self.session.commit()
        return {"rejected": True}

    async def cancel_user_publish(
        self,
        user_id: int,
        course_id: int,
        upload_id: int,
    ) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_user_upload(user_id, course_id, upload_id)
        return await self._make_upload_private(upload)

    async def unpublish_upload(self, upload_id: int) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_upload(upload_id)
        return await self._make_upload_private(upload)

    async def delete_user_upload(
        self,
        user_id: int,
        course_id: int,
        upload_id: int,
    ) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_user_upload(user_id, course_id, upload_id)
        return await self._delete_upload(upload)

    async def delete_upload(self, upload_id: int) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_upload(upload_id)
        return await self._delete_upload(upload)

    async def mark_upload_failed(
        self,
        upload_id: int,
        message: str,
    ) -> None:
        upload = await self.upload_repo.get_upload_by_id(upload_id)
        if not upload:
            return
        staged_path = upload.staged_path
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.FAILED,
            staged_path=None,
            error_message=message[:500],
        )
        await self.session.commit()
        await self._remove_staged_file(staged_path)

    async def process_upload(self, upload_id: int) -> None:
        upload = await self._load_upload(upload_id)
        if upload.upload_status == MaterialUploadStatus.COMPLETED:
            return
        if not upload.staged_path:
            raise StudyMaterialValidationError("Staged upload file is missing")
        staged_path = upload.staged_path
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.UPLOADING,
            error_message=None,
        )
        await self.session.commit()
        await self.storage.ensure_bucket()
        await self.storage.upload_file(
            upload.staged_path,
            upload.storage_key,
            upload.content_type,
        )
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.COMPLETED,
            staged_path=None,
            error_message=None,
        )
        await self.session.commit()
        await self._remove_staged_file(staged_path)

    async def _create_upload(
        self,
        user_id: int,
        offering,
        week: int,
        request_shared_library: bool,
        file: UploadFile,
    ) -> StudyMaterialUpload:
        filename = self._validate_file(file)
        payload = await file.read()
        if not payload:
            raise StudyMaterialValidationError("Uploaded file is empty")
        if len(payload) > MAX_FILE_SIZE:
            raise StudyMaterialValidationError("File size exceeds 25MB")
        storage_key = self._storage_key(offering.course.title, week, filename)
        staged_path = await self._stage_file(filename, payload)
        return await self.upload_repo.create(
            course_id=offering.id,
            uploader_id=user_id,
            user_week=week,
            original_filename=filename,
            staged_path=staged_path,
            storage_key=storage_key,
            content_type=self._content_type(file, filename),
            file_size_bytes=len(payload),
            upload_status=MaterialUploadStatus.QUEUED,
            curation_status=self._curation_status(request_shared_library),
            error_message=None,
        )

    async def _require_course_access(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        if await self.upload_repo.get_enrolled_course(user_id, course_id):
            return
        raise StudyMaterialForbiddenError()

    async def _load_upload(self, upload_id: int) -> StudyMaterialUpload:
        upload = await self.upload_repo.get_upload_by_id(upload_id)
        if upload:
            return upload
        raise StudyMaterialNotFoundError()

    async def _load_user_upload(
        self,
        user_id: int,
        course_id: int,
        upload_id: int,
    ) -> StudyMaterialUpload:
        await self._require_course_access(user_id, course_id)
        upload = await self._load_upload(upload_id)
        if upload.course_id == course_id and upload.uploader_id == user_id:
            return upload
        raise StudyMaterialNotFoundError()

    async def _serialize_uploads(
        self,
        uploads: list[StudyMaterialUpload | None],
    ) -> list[dict]:
        payload = []
        for upload in uploads:
            if not upload:
                continue
            url = await self._download_url(upload.storage_key, upload.upload_status)
            payload.append(_upload_response(upload, url))
        return payload

    async def _serialize_library(
        self,
        entries: list[StudyMaterialLibraryEntry],
        user_id: int,
    ) -> list[dict]:
        payload = []
        for entry in entries:
            url = await self.storage.generate_download_url(entry.upload.storage_key)
            payload.append(_library_response(entry, url, user_id))
        return payload

    async def _download_url(
        self,
        storage_key: str,
        upload_status: MaterialUploadStatus,
    ) -> str | None:
        if upload_status != MaterialUploadStatus.COMPLETED:
            return None
        return await self.storage.generate_download_url(storage_key)

    def _enqueue_uploads(self, uploads: list[StudyMaterialUpload]) -> None:
        from nutrack.tasks.materials import upload_course_material_task

        try:
            for upload in uploads:
                upload_course_material_task.delay(upload.id)
        except Exception as exc:  # pragma: no cover - broker/network failure
            raise StudyMaterialQueueError() from exc

    def _validate_batch(self, week: int, files: list[UploadFile]) -> None:
        self._validate_week(week)
        if not files:
            raise StudyMaterialValidationError("Select at least one file")
        if len(files) > MAX_FILES_PER_BATCH:
            raise StudyMaterialValidationError("You can upload up to 10 files at once")

    def _validate_week(self, week: int) -> None:
        if 1 <= week <= 15:
            return
        raise StudyMaterialValidationError("Week must be between 1 and 15")

    def _validate_file(self, file: UploadFile) -> str:
        filename = (file.filename or "").strip()
        suffix = Path(filename).suffix.lower()
        if filename and suffix in ALLOWED_EXTENSIONS:
            return filename
        raise StudyMaterialValidationError("Unsupported file type")

    def _content_type(self, file: UploadFile, filename: str) -> str:
        return file.content_type or ALLOWED_EXTENSIONS[Path(filename).suffix.lower()]

    def _storage_key(self, course_title: str, week: int, filename: str) -> str:
        safe_name = sanitize_filename(filename)
        return f"{slugify(course_title)}/week_{week}/{uuid4()}__{safe_name}"

    async def _stage_file(self, filename: str, payload: bytes) -> str:
        directory = Path(settings.MATERIAL_UPLOAD_STAGING_DIR)
        await asyncio.to_thread(directory.mkdir, parents=True, exist_ok=True)
        path = directory / f"{uuid4()}__{sanitize_filename(filename)}"
        await asyncio.to_thread(path.write_bytes, payload)
        return str(path)

    async def _remove_staged_file(self, staged_path: str | None) -> None:
        if not staged_path:
            return
        path = Path(staged_path)
        if not path.exists():
            return
        await asyncio.to_thread(path.unlink)

    async def _delete_storage_file(self, storage_key: str | None) -> None:
        if not storage_key:
            return
        try:
            await self.storage.delete_file(storage_key)
        except Exception:
            return

    async def _mark_queue_failure(
        self,
        uploads: list[StudyMaterialUpload],
    ) -> None:
        for upload in uploads:
            staged_path = upload.staged_path
            await self.upload_repo.update(
                upload,
                upload_status=MaterialUploadStatus.FAILED,
                staged_path=None,
                error_message="Failed to queue material upload",
            )
            await self._remove_staged_file(staged_path)
        await self.session.commit()

    def _curation_status(
        self,
        request_shared_library: bool,
    ) -> MaterialCurationStatus:
        if request_shared_library:
            return MaterialCurationStatus.PENDING
        return MaterialCurationStatus.NOT_REQUESTED

    async def _make_upload_private(
        self,
        upload: StudyMaterialUpload,
    ) -> dict:
        await self._delete_library_entry(upload)
        await self.upload_repo.update(
            upload,
            curation_status=MaterialCurationStatus.NOT_REQUESTED,
        )
        await self.session.commit()
        loaded = await self.upload_repo.get_upload_by_id(upload.id)
        return _upload_response(
            loaded,
            await self._download_url(loaded.storage_key, loaded.upload_status),
        )

    async def _delete_upload(
        self,
        upload: StudyMaterialUpload,
    ) -> dict:
        staged_path = upload.staged_path
        storage_key = upload.storage_key
        await self._delete_library_entry(upload)
        await self.upload_repo.delete(upload)
        await self.session.commit()
        await self._remove_staged_file(staged_path)
        await self._delete_storage_file(storage_key)
        return {"deleted": True}

    async def _delete_library_entry(
        self,
        upload: StudyMaterialUpload,
    ) -> None:
        if upload.library_entry is None:
            return
        await self.library_repo.delete(upload.library_entry)

    async def _cleanup_stale_uploads(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=STALE_UPLOAD_MINUTES)
        statuses = (
            MaterialUploadStatus.QUEUED,
            MaterialUploadStatus.UPLOADING,
        )
        uploads = await self.upload_repo.list_stale_uploads(cutoff, statuses)
        if not uploads:
            return
        for upload in uploads:
            await self._fail_stale_upload(upload)
        await self.session.commit()

    async def _fail_stale_upload(
        self,
        upload: StudyMaterialUpload,
    ) -> None:
        staged_path = upload.staged_path
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.FAILED,
            staged_path=None,
            error_message="Upload timed out before completion",
        )
        await self._remove_staged_file(staged_path)
        await self._delete_storage_file(upload.storage_key)
