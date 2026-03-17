import asyncio
import logging
import os
import uuid
from collections import Counter
from pathlib import Path

from fastapi import UploadFile

from nutrack.config import settings
from nutrack.courses.exceptions import (
    CourseScheduleFileError,
    CourseScheduleParsingError,
)
from nutrack.courses.domain import CourseEntity
from nutrack.courses.parser import parse_pdf_courses
from nutrack.courses.repository import CourseRepository
from nutrack.courses.schemas import CourseSearchItem
from nutrack.semester import normalize_term

MAX_FILE_SIZE = 10 * 1024 * 1024
UPLOAD_DIR = Path("/tmp/schedule_uploads")
PDF_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}

logger = logging.getLogger(__name__)


def _course_option(course) -> CourseSearchItem:
    return CourseSearchItem(
        id=course.id,
        code=course.code,
        level=course.level,
        section=course.section,
        title=course.title,
        ects=course.ects,
        term=course.term,
        year=course.year,
        meeting_time=course.meeting_time,
        room=course.room,
    )


def _remove_tmp_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return


def _log_duplicate_keys(courses: list[CourseEntity]) -> None:
    keys = Counter(
        (
            course.code,
            course.level,
            course.section,
            course.term,
            course.year,
        )
        for course in courses
    )
    duplicates = [
        (code, level, section, term, year, count)
        for (code, level, section, term, year), count in keys.items()
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
        term: str,
        year: int,
    ) -> dict[str, int | list[dict[str, object]]]:
        normalized_term = normalize_term(term)
        logger.info(
            "Course schedule upload started.",
            extra={
                "filename": file.filename,
                "content_type": file.content_type,
                "term": normalized_term,
                "year": year,
            },
        )
        payload = await self._read_payload(file)
        path = self._store_tmp_file(payload)
        try:
            courses, invalid_rows = await self._parse_pdf(path)
            scoped_courses = [
                course.model_copy(update={"term": normalized_term, "year": year})
                for course in courses
            ]
            result = await self._upsert_courses(scoped_courses)
            result["term"] = normalized_term
            result["year"] = year
            result["invalid_rows"] = invalid_rows
            result["invalid_rows_count"] = len(invalid_rows)
            logger.info(
                "Course schedule upload completed.",
                extra={
                    "processed_rows": result["processed_rows"],
                    "inserted_count": result["inserted_count"],
                    "updated_count": result["updated_count"],
                    "invalid_rows_count": result["invalid_rows_count"],
                    "term": normalized_term,
                    "year": year,
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
                course.term,
                course.year,
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


class CourseSearchService:
    def __init__(self, repository: CourseRepository) -> None:
        self.repository = repository

    async def search_courses(
        self,
        query: str | None,
        limit: int = 10,
        term: str | None = None,
        year: int | None = None,
    ) -> list[CourseSearchItem]:
        resolved_term, resolved_year = self._resolve_term_year(term, year)
        bounded_limit = min(max(limit, 1), 20)
        courses = await self.repository.search(
            query,
            bounded_limit,
            resolved_term,
            resolved_year,
        )
        return [_course_option(course) for course in courses]

    def _resolve_term_year(
        self,
        term: str | None,
        year: int | None,
    ) -> tuple[str, int]:
        if term is None and year is None:
            return (settings.CURRENT_TERM, settings.CURRENT_YEAR)
        if term is None or year is None:
            raise ValueError("term and year must be provided together")
        return (normalize_term(term), year)
