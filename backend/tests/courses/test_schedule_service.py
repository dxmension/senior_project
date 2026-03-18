from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import UploadFile
from starlette.datastructures import Headers

from nutrack.courses.domain import CourseEntity
from nutrack.courses.exceptions import (
    CourseScheduleFileError,
    CourseScheduleParsingError,
)
from nutrack.courses.service import CourseScheduleService


def _upload_file(payload: bytes = b"pdf") -> UploadFile:
    return UploadFile(
        filename="schedule.pdf",
        file=BytesIO(payload),
        headers=Headers({"content-type": "application/pdf"}),
    )


def _schedule_service() -> CourseScheduleService:
    course_repository = SimpleNamespace(
        get_by_code_and_level=AsyncMock(),
        create=AsyncMock(),
        update=AsyncMock(),
    )
    offering_repository = SimpleNamespace(
        get_by_code_level_and_section=AsyncMock(),
        create=AsyncMock(),
        update=AsyncMock(),
    )
    return CourseScheduleService(
        course_repository=course_repository,
        offering_repository=offering_repository,
    )


@pytest.mark.asyncio
async def test_read_payload_rejects_empty_file() -> None:
    service = _schedule_service()

    with pytest.raises(CourseScheduleFileError, match="empty"):
        await service._read_payload(_upload_file(b""))  # noqa: SLF001


@pytest.mark.asyncio
async def test_parse_pdf_maps_value_error() -> None:
    service = _schedule_service()

    with pytest.raises(CourseScheduleParsingError, match="bad file"):
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(
                "nutrack.courses.service.parse_pdf_courses",
                lambda path: (_ for _ in ()).throw(ValueError("bad file")),
            )
            await service._parse_pdf("/tmp/schedule.pdf")  # noqa: SLF001


@pytest.mark.asyncio
async def test_upsert_courses_counts_inserts_and_updates() -> None:
    service = _schedule_service()
    first_course = SimpleNamespace(id=3)
    second_course = SimpleNamespace(id=4)
    existing = SimpleNamespace(id=9)
    service.course_repository.get_by_code_and_level = AsyncMock(
        side_effect=[first_course, second_course]
    )
    service.course_repository.update = AsyncMock(
        side_effect=lambda course, **kwargs: course
    )
    service.offering_repository.get_by_identity = AsyncMock(
        side_effect=[None, existing]
    )
    courses = [
        CourseEntity(
            code="CSCI",
            level="151",
            title="Programming",
            ects=6,
            section="1",
        ),
        CourseEntity(
            code="MATH",
            level="161",
            title="Calculus",
            ects=5,
            section="2",
        ),
    ]

    result = await service._upsert_courses(courses, "Fall", 2026)  # noqa: SLF001

    assert result == {
        "processed_rows": 2,
        "inserted_count": 1,
        "updated_count": 1,
    }
    service.offering_repository.create.assert_awaited_once()
    service.offering_repository.update.assert_awaited_once_with(
        existing,
        course_id=4,
        term="Fall",
        year=2026,
        section="2",
        start_date=None,
        end_date=None,
        days=None,
        meeting_time=None,
        enrolled=None,
        capacity=None,
        faculty=None,
        room=None,
    )


@pytest.mark.asyncio
async def test_ingest_removes_tmp_file_after_processing(monkeypatch) -> None:
    service = _schedule_service()
    cleanup: list[str] = []
    course = CourseEntity(
        code="CSCI",
        level="151",
        title="Programming",
        ects=6,
        section="1",
    )
    service._read_payload = AsyncMock(return_value=b"pdf")
    monkeypatch.setattr(
        "nutrack.courses.service._remove_tmp_file",
        lambda path: cleanup.append(path),
    )
    monkeypatch.setattr(service, "_store_tmp_file", lambda payload: "/tmp/test.pdf")
    monkeypatch.setattr(service, "_parse_pdf", AsyncMock(return_value=([course], [])))
    monkeypatch.setattr(
        service,
        "_upsert_courses",
        AsyncMock(
            return_value={
                "processed_rows": 1,
                "inserted_count": 1,
                "updated_count": 0,
            }
        ),
    )

    result = await service.ingest(_upload_file(), "fall", 2026)

    assert result["term"] == "Fall"
    assert result["year"] == 2026
    assert cleanup == ["/tmp/test.pdf"]
