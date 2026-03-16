import asyncio
import logging
import os
import uuid
from collections import Counter
from pathlib import Path

from fastapi import UploadFile

from nutrack.courses.exceptions import (
    CourseScheduleFileError,
    CourseScheduleParsingError,
)
from nutrack.courses.repository import CourseRepository
from nutrack.courses.domain import CourseEntity
from nutrack.courses.parser import parse_pdf_courses

MAX_FILE_SIZE = 10 * 1024 * 1024
UPLOAD_DIR = Path("/tmp/schedule_uploads")
PDF_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}

logger = logging.getLogger(__name__)


def _remove_tmp_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return


def _log_duplicate_keys(courses: list[CourseEntity]) -> None:
    keys = Counter(
        (course.code, course.level, course.section)
        for course in courses
    )
    duplicates = [
        (code, level, section, count)
        for (code, level, section), count in keys.items()
        if count > 1
    ]
    if not duplicates:
        return
    sample = duplicates[:10]
    logger.warning(
        "Duplicate course keys found in parsed file.",
        extra={"duplicate_keys_count": len(duplicates), "sample_keys": sample},
    )


class CourseScheduleService:
    def __init__(
        self,
        repository: CourseRepository,
    ):
        self.repository = repository
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    async def ingest(
        self,
        file: UploadFile,
    ) -> dict[str, int | list[dict[str, object]]]:
        logger.info(
            "Course schedule upload started.",
            extra={"filename": file.filename, "content_type": file.content_type},
        )
        payload = await self._read_payload(file)
        path = self._store_tmp_file(payload)
        try:
            courses, invalid_rows = await self._parse_pdf(path)
            result = await self._upsert_courses(courses)
            result["invalid_rows"] = invalid_rows
            result["invalid_rows_count"] = len(invalid_rows)
            logger.info(
                "Course schedule upload completed.",
                extra={
                    "processed_rows": result["processed_rows"],
                    "inserted_count": result["inserted_count"],
                    "updated_count": result["updated_count"],
                    "invalid_rows_count": result["invalid_rows_count"],
                },
            )
            return result
        finally:
            _remove_tmp_file(path)

    async def _read_payload(self, file: UploadFile) -> bytes:
        self._validate_file_type(file)
        payload = await file.read()
        if not payload:
            raise CourseScheduleFileError("Uploaded file is empty.")
        if len(payload) > MAX_FILE_SIZE:
            raise CourseScheduleFileError("File size exceeds 10MB.")
        return payload

    def _validate_file_type(self, file: UploadFile) -> None:
        name = (file.filename or "").lower()
        content_type = (file.content_type or "").lower()
        if not name.endswith(".pdf"):
            raise CourseScheduleFileError("Only PDF files are supported.")
        if content_type and content_type not in PDF_TYPES:
            raise CourseScheduleFileError("Invalid content type for PDF file.")

    def _store_tmp_file(self, payload: bytes) -> str:
        filename = f"{uuid.uuid4()}.pdf"
        path = UPLOAD_DIR / filename
        with path.open("wb") as handle:
            handle.write(payload)
        return str(path)

    async def _parse_pdf(
        self,
        file_path: str,
    ) -> tuple[list[CourseEntity], list[dict[str, object]]]:
        try:
            return await asyncio.to_thread(parse_pdf_courses, file_path)
        except ValueError as exc:
            raise CourseScheduleParsingError(str(exc)) from exc
        except Exception as exc:
            raise CourseScheduleParsingError(
                "Failed to parse course schedule."
            ) from exc

    async def _upsert_courses(
        self,
        courses: list[CourseEntity],
    ) -> dict[str, int]:
        inserted = 0
        updated = 0
        _log_duplicate_keys(courses)
        for course in courses:
            existing = await self.repository.get_by_code_level_and_section(
                course.code,
                course.level,
                course.section,
            )
            if not existing:
                await self.repository.create(**course.model_dump())
                inserted += 1
                continue
            await self.repository.update(existing, **course.model_dump())
            updated += 1
        return {
            "processed_rows": len(courses),
            "inserted_count": inserted,
            "updated_count": updated,
        }
