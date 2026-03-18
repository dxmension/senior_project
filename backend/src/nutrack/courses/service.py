import asyncio
import logging
import os
import uuid
from collections import Counter
from pathlib import Path

from fastapi import UploadFile

from nutrack.config import settings
from nutrack.courses.domain import CourseEntity
from nutrack.courses.exceptions import (
    CourseScheduleFileError,
    CourseScheduleParsingError,
)
from nutrack.courses.parser import parse_pdf_courses
from nutrack.courses.repository import CourseOfferingRepository, CourseRepository
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


def _canonical_payload(course: CourseEntity) -> dict[str, object]:
    return {
        "code": course.code,
        "level": course.level,
        "title": course.title,
        "department": course.department,
        "ects": course.ects,
        "description": course.description,
        "school": course.school,
        "academic_level": course.academic_level,
        "credits_us": course.credits_us,
    }


def _offering_payload(
    course: CourseEntity,
    course_id: int,
    term: str,
    year: int,
) -> dict[str, object]:
    return {
        "course_id": course_id,
        "term": term,
        "year": year,
        "section": course.section,
        "start_date": course.start_date,
        "end_date": course.end_date,
        "days": course.days,
        "meeting_time": course.meeting_time,
        "enrolled": course.enrolled,
        "capacity": course.capacity,
        "faculty": course.faculty,
        "room": course.room,
    }


def _course_option(offering) -> CourseSearchItem:
    course = offering.course
    return CourseSearchItem(
        id=offering.id,
        code=course.code,
        level=course.level,
        section=offering.section,
        title=course.title,
        ects=course.ects,
        term=offering.term,
        year=offering.year,
        meeting_time=offering.meeting_time,
        room=offering.room,
    )


def _remove_tmp_file(file_path: str) -> None:
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return


def _log_duplicate_keys(
    courses: list[CourseEntity],
    term: str,
    year: int,
) -> None:
    keys = Counter((course.code, course.level, course.section, term, year) for course in courses)
    duplicates = [
        (code, level, section, dup_term, dup_year, count)
        for (code, level, section, dup_term, dup_year), count in keys.items()
        if count > 1
    ]
    if not duplicates:
        return
    logger.warning(
        "Duplicate course keys found in parsed file.",
        extra={
            "duplicate_keys_count": len(duplicates),
            "sample_keys": duplicates[:10],
        },
    )


class CourseScheduleService:
    def __init__(
        self,
        course_repository: CourseRepository,
        offering_repository: CourseOfferingRepository,
    ):
        self.course_repository = course_repository
        self.offering_repository = offering_repository
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
            result = await self._upsert_courses(courses, normalized_term, year)
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
        term: str,
        year: int,
    ) -> dict[str, int]:
        inserted = 0
        updated = 0
        _log_duplicate_keys(courses, term, year)
        for parsed in courses:
            course = await self._upsert_course(parsed)
            offering = await self.offering_repository.get_by_identity(
                course.id,
                term,
                year,
                parsed.section,
            )
            payload = _offering_payload(parsed, course.id, term, year)
            if not offering:
                await self.offering_repository.create(**payload)
                inserted += 1
                continue
            await self.offering_repository.update(offering, **payload)
            updated += 1
        return {
            "processed_rows": len(courses),
            "inserted_count": inserted,
            "updated_count": updated,
        }

    async def _upsert_course(self, parsed: CourseEntity):
        course = await self.course_repository.get_by_code_and_level(
            parsed.code,
            parsed.level,
        )
        payload = _canonical_payload(parsed)
        if not course:
            return await self.course_repository.create(**payload)
        return await self.course_repository.update(course, **payload)


class CourseSearchService:
    def __init__(self, repository: CourseOfferingRepository) -> None:
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
        offerings = await self.repository.search(
            query,
            bounded_limit,
            resolved_term,
            resolved_year,
        )
        return [_course_option(offering) for offering in offerings]

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
