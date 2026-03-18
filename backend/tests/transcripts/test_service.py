from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from nutrack.transcripts.exceptions import (
    FileValidationError,
    TranscriptUploadNotFoundError,
)
from nutrack.transcripts.service import TranscriptService


def _upload_file(
    filename: str,
    content_type: str,
    payload: bytes = b"pdf",
) -> UploadFile:
    return UploadFile(
        filename=filename,
        file=BytesIO(payload),
        headers=Headers({"content-type": content_type}),
    )


def _service() -> TranscriptService:
    redis = SimpleNamespace(
        hset=AsyncMock(),
        expire=AsyncMock(),
        hgetall=AsyncMock(),
    )
    service = TranscriptService(session=None, redis=redis)
    service.user_repo.get_by_name = AsyncMock()
    service.user_repo.get_by_id = AsyncMock()
    service.user_repo.update = AsyncMock()
    service.course_repo.get_or_create = AsyncMock()
    service.offering_repo.get_or_create = AsyncMock()
    service.enrollment_repo.get_by_user_and_course = AsyncMock()
    service.enrollment_repo.create = AsyncMock()
    return service


@pytest.mark.asyncio
async def test_get_upload_status_raises_for_missing_upload() -> None:
    service = _service()
    service.redis.hgetall = AsyncMock(return_value={})

    with pytest.raises(TranscriptUploadNotFoundError):
        await service.get_upload_status("missing")


@pytest.mark.asyncio
async def test_upload_rejects_non_pdf_file() -> None:
    service = _service()
    service._set_upload_status = AsyncMock()
    file = _upload_file("transcript.txt", "text/plain")

    with pytest.raises(FileValidationError, match="Only PDF"):
        await service.upload(1, file)

    assert service._set_upload_status.await_args_list[1].args == (
        service._set_upload_status.await_args_list[1].args[0],
        "failed",
        "Only PDF files are accepted",
    )


@pytest.mark.asyncio
async def test_upload_rejects_transcript_for_other_user(monkeypatch) -> None:
    service = _service()
    service._set_upload_status = AsyncMock()
    user = SimpleNamespace(id=2, study_year=3)
    service.user_repo.get_by_name = AsyncMock(return_value=user)
    file = _upload_file("transcript.pdf", "application/pdf")
    monkeypatch.setattr(
        "nutrack.transcripts.service.parse_transcript_from_bytes",
        lambda payload: {
            "student_name": "Doe John",
            "enrollment_year": 2024,
            "major": "CS",
            "overall_gpa": 3.7,
            "credits_earned": 30,
            "credits_enrolled": 36,
            "courses": [{"course_code": "CSCI 151", "term": "Fall", "year": 2025}],
        },
    )

    with pytest.raises(FileValidationError, match="not your own transcript"):
        await service.upload(1, file)


@pytest.mark.asyncio
async def test_upload_updates_user_and_creates_enrollments(monkeypatch) -> None:
    service = _service()
    service._set_upload_status = AsyncMock()
    user = SimpleNamespace(id=1, study_year=2)
    course = SimpleNamespace(id=10)
    offering = SimpleNamespace(id=20)
    service.user_repo.get_by_name = AsyncMock(return_value=user)
    service.course_repo.get_or_create = AsyncMock(return_value=course)
    service.offering_repo.get_or_create = AsyncMock(return_value=offering)
    file = _upload_file("transcript.pdf", "application/pdf")
    monkeypatch.setattr(
        "nutrack.transcripts.service.parse_transcript_from_bytes",
        lambda payload: {
            "student_name": "Doe John",
            "major": "Computer Science",
            "overall_gpa": 3.8,
            "credits_earned": 40,
            "credits_enrolled": 48,
            "enrollment_year": 2024,
            "courses": [
                {
                    "course_code": "CSCI 151",
                    "course_title": "Programming",
                    "term": "fall",
                    "year": 2025,
                    "grade": "A",
                    "grade_points": 4.0,
                    "ects": 6,
                }
            ],
        },
    )

    upload_id = await service.upload(1, file)

    assert upload_id
    service.user_repo.update.assert_awaited_once()
    service.course_repo.get_or_create.assert_awaited_once_with(
        "CSCI",
        "151",
        defaults={
            "title": "Programming",
            "department": "CSCI",
            "ects": 6,
        },
    )
    service.offering_repo.get_or_create.assert_awaited_once_with(
        10,
        "Fall",
        2025,
        None,
        defaults={},
    )
    service.enrollment_repo.create.assert_awaited_once()
    assert service._set_upload_status.await_args_list[-1].args[1] == "completed"


@pytest.mark.asyncio
async def test_save_manual_entries_requires_existing_user() -> None:
    service = _service()
    service.user_repo.get_by_id = AsyncMock(return_value=None)

    with pytest.raises(FileValidationError, match="User not found"):
        await service.save_manual_entries(1, {"courses": [{}]})


@pytest.mark.asyncio
async def test_save_manual_entries_skips_duplicates_and_blank_rows() -> None:
    service = _service()
    user = SimpleNamespace(major="CS")
    course = SimpleNamespace(id=5)
    offering = SimpleNamespace(id=9)
    service.user_repo.get_by_id = AsyncMock(return_value=user)
    service.course_repo.get_or_create = AsyncMock(return_value=course)
    service.offering_repo.get_or_create = AsyncMock(return_value=offering)
    service.enrollment_repo.get_by_user_and_course = AsyncMock(
        side_effect=[SimpleNamespace(id=1), None]
    )

    await service.save_manual_entries(
        1,
        {
            "major": "Math",
            "courses": [
                {
                    "code": "CSCI 151",
                    "title": "Programming",
                    "term": "Fall",
                    "year": 2025,
                    "grade": "A",
                    "grade_points": 4.0,
                    "ects": 6,
                },
                {
                    "code": "   ",
                    "title": "",
                    "term": "Fall",
                    "year": 2025,
                    "grade": "",
                    "grade_points": 0,
                    "ects": 3,
                },
            ],
        },
    )

    service.user_repo.update.assert_awaited_once_with(
        user,
        major="Math",
        is_onboarded=True,
    )
    service.enrollment_repo.create.assert_not_called()


@pytest.mark.parametrize(
    ("raw_code", "expected"),
    [("CSCI 151", ("CSCI", "151")), ("nusm411a", ("NUSM", "411A")), ("BIO", ("BIO", "0"))],
)
def test_parse_course_identity_extracts_code_and_level(
    raw_code: str,
    expected: tuple[str, str],
) -> None:
    service = _service()

    assert service._parse_course_identity(raw_code) == expected  # noqa: SLF001


def test_course_year_requires_supported_integer() -> None:
    service = _service()

    with pytest.raises(FileValidationError, match="Course year is required"):
        service._course_year({"year": "1999"})  # noqa: SLF001
