from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from nutrack.study.models import MaterialCurationStatus, MaterialUploadStatus
from nutrack.study.service import StudyService


def _upload_file(
    name: str = "notes.pdf",
    content_type: str = "application/pdf",
) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(b"payload"), headers={"content-type": content_type})


@pytest.mark.asyncio
async def test_queue_uploads_commits_and_enqueues(monkeypatch) -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    offering = SimpleNamespace(
        id=7,
        course=SimpleNamespace(title="Intro to Programming"),
    )
    upload = SimpleNamespace(id=11)
    service.upload_repo = SimpleNamespace(
        get_enrolled_course=AsyncMock(return_value=offering),
        get_upload_by_id=AsyncMock(return_value=upload),
    )
    service._create_upload = AsyncMock(return_value=upload)
    service._cleanup_stale_uploads = AsyncMock()
    service._enqueue_uploads = Mock()
    service._serialize_uploads = AsyncMock(return_value=[{"id": 11}])

    result = await service.queue_uploads(1, 7, 4, False, [_upload_file()])

    assert result == [{"id": 11}]
    session.commit.assert_awaited_once()
    service._enqueue_uploads.assert_called_once_with([upload])


@pytest.mark.asyncio
async def test_publish_upload_creates_library_entry() -> None:
    session = AsyncMock()
    storage = AsyncMock()
    storage.generate_download_url = AsyncMock(return_value="http://example.com/file")
    service = StudyService(session=session, storage=storage)
    upload = SimpleNamespace(
        id=8,
        course_id=7,
        uploader_id=1,
        storage_key="course/week_5/file.pdf",
        upload_status=MaterialUploadStatus.COMPLETED,
        curation_status=MaterialCurationStatus.PENDING,
    )
    entry = SimpleNamespace(
        id=3,
        upload=SimpleNamespace(
            id=8,
            uploader_id=1,
            storage_key="course/week_5/file.pdf",
            original_filename="file.pdf",
            content_type="application/pdf",
            file_size_bytes=1024,
            course_offering=SimpleNamespace(
                course=SimpleNamespace(code="CSCI", level="151", title="Programming")
            ),
        ),
        course_id=7,
        curated_week=5,
        curated_title="Week 5 slides",
        updated_at="2026-04-12T10:00:00Z",
    )
    service._load_upload = AsyncMock(return_value=upload)
    service._cleanup_stale_uploads = AsyncMock()
    service.library_repo = SimpleNamespace(
        get_by_upload_id=AsyncMock(side_effect=[None, entry]),
        create=AsyncMock(return_value=entry),
        update=AsyncMock(),
    )
    service.upload_repo = SimpleNamespace(update=AsyncMock())

    result = await service.publish_upload(99, 8, "Week 5 slides", 5)

    assert result["title"] == "Week 5 slides"
    assert result["download_url"] == "http://example.com/file"
    service.library_repo.create.assert_awaited_once()
    service.upload_repo.update.assert_awaited_once_with(
        upload,
        curation_status=MaterialCurationStatus.PUBLISHED,
    )


@pytest.mark.asyncio
async def test_list_admin_uploads_hides_private_and_rejected_items() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(
        storage_key="course/week_5/file.pdf",
        course_offering=SimpleNamespace(
            course=SimpleNamespace(code="CSCI", level="151", title="Programming")
        ),
        uploader=SimpleNamespace(
            id=7,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        ),
        library_entry=None,
        id=8,
        course_id=7,
        user_week=5,
        original_filename="file.pdf",
        content_type="application/pdf",
        file_size_bytes=1024,
        upload_status=MaterialUploadStatus.COMPLETED,
        curation_status=MaterialCurationStatus.PENDING,
        error_message=None,
        created_at="2026-04-12T10:00:00Z",
        updated_at="2026-04-12T10:00:00Z",
    )
    service._cleanup_stale_uploads = AsyncMock()
    service._download_url = AsyncMock(return_value="http://example.com/file")
    service.upload_repo = SimpleNamespace(
        list_admin_uploads=AsyncMock(return_value=[upload]),
    )

    result = await service.list_admin_uploads()

    assert result[0]["curation_status"] == "pending"
    service.upload_repo.list_admin_uploads.assert_awaited_once_with(
        course_id=None,
        user_id=None,
        upload_status=None,
        curation_statuses=(
            MaterialCurationStatus.PENDING,
            MaterialCurationStatus.PUBLISHED,
        ),
    )


@pytest.mark.asyncio
async def test_list_admin_uploads_ignores_private_filter() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    service._cleanup_stale_uploads = AsyncMock()
    service.upload_repo = SimpleNamespace(list_admin_uploads=AsyncMock())

    result = await service.list_admin_uploads(
        curation_status=MaterialCurationStatus.NOT_REQUESTED,
    )

    assert result == []
    service.upload_repo.list_admin_uploads.assert_not_called()


@pytest.mark.asyncio
async def test_mark_upload_failed_clears_staged_path() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(staged_path="/tmp/upload", id=9)
    service.upload_repo = SimpleNamespace(
        get_upload_by_id=AsyncMock(return_value=upload),
        update=AsyncMock(),
    )
    service._remove_staged_file = AsyncMock()

    await service.mark_upload_failed(9, "boom")

    service.upload_repo.update.assert_awaited_once_with(
        upload,
        upload_status=MaterialUploadStatus.FAILED,
        staged_path=None,
        error_message="boom",
    )
    service._remove_staged_file.assert_awaited_once_with("/tmp/upload")


@pytest.mark.asyncio
async def test_create_upload_sets_private_curation_status() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    offering = SimpleNamespace(id=7, course=SimpleNamespace(title="Programming"))
    service._stage_file = AsyncMock(return_value="/tmp/upload")
    service.upload_repo = SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace()))

    await service._create_upload(1, offering, 3, False, _upload_file())  # noqa: SLF001

    assert service.upload_repo.create.await_args.kwargs["curation_status"] == (
        MaterialCurationStatus.NOT_REQUESTED
    )


@pytest.mark.asyncio
async def test_delete_upload_removes_library_entry_and_files() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(
        id=8,
        staged_path="/tmp/upload",
        storage_key="course/file.pdf",
        library_entry=SimpleNamespace(id=2),
    )
    service.upload_repo = SimpleNamespace(delete=AsyncMock())
    service.library_repo = SimpleNamespace(delete=AsyncMock())
    service._remove_staged_file = AsyncMock()
    service._delete_storage_file = AsyncMock()

    result = await service._delete_upload(upload)  # noqa: SLF001

    assert result == {"deleted": True}
    service.library_repo.delete.assert_awaited_once_with(upload.library_entry)
    service.upload_repo.delete.assert_awaited_once_with(upload)
    service._remove_staged_file.assert_awaited_once_with("/tmp/upload")
    service._delete_storage_file.assert_awaited_once_with("course/file.pdf")


@pytest.mark.asyncio
async def test_make_upload_private_deletes_library_entry() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(
        id=8,
        storage_key="course/file.pdf",
        upload_status=MaterialUploadStatus.COMPLETED,
        library_entry=SimpleNamespace(id=5),
    )
    loaded = SimpleNamespace(
        id=8,
        course_id=7,
        uploader_id=1,
        user_week=2,
        original_filename="file.pdf",
        content_type="application/pdf",
        file_size_bytes=10,
        upload_status=MaterialUploadStatus.COMPLETED,
        curation_status=MaterialCurationStatus.NOT_REQUESTED,
        error_message=None,
        library_entry=None,
        storage_key="course/file.pdf",
        created_at="2026-04-12T10:00:00Z",
        updated_at="2026-04-12T10:00:00Z",
        course_offering=SimpleNamespace(
            course=SimpleNamespace(code="CSCI", level="151", title="Programming")
        ),
    )
    service.upload_repo = SimpleNamespace(
        update=AsyncMock(),
        get_upload_by_id=AsyncMock(return_value=loaded),
    )
    service.library_repo = SimpleNamespace(delete=AsyncMock())
    service._download_url = AsyncMock(return_value="http://example.com/file")

    result = await service._make_upload_private(upload)  # noqa: SLF001

    assert result["publish_requested"] is False
    service.upload_repo.update.assert_awaited_once_with(
        upload,
        curation_status=MaterialCurationStatus.NOT_REQUESTED,
    )


@pytest.mark.asyncio
async def test_cleanup_stale_uploads_marks_old_items_failed() -> None:
    session = AsyncMock()
    service = StudyService(session=session, storage=AsyncMock())
    stale = SimpleNamespace(
        staged_path="/tmp/upload",
        storage_key="course/file.pdf",
    )
    cutoff_check = {}

    async def list_stale_uploads(cutoff, statuses):
        cutoff_check["cutoff"] = cutoff
        cutoff_check["statuses"] = statuses
        return [stale]

    service.upload_repo = SimpleNamespace(
        list_stale_uploads=AsyncMock(side_effect=list_stale_uploads),
        update=AsyncMock(),
    )
    service._remove_staged_file = AsyncMock()
    service._delete_storage_file = AsyncMock()

    await service._cleanup_stale_uploads()  # noqa: SLF001

    assert cutoff_check["cutoff"] < datetime.now(timezone.utc)
    assert MaterialUploadStatus.QUEUED in cutoff_check["statuses"]
    service.upload_repo.update.assert_awaited_once_with(
        stale,
        upload_status=MaterialUploadStatus.FAILED,
        staged_path=None,
        error_message="Upload timed out before completion",
    )
