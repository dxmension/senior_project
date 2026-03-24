import asyncio
import logging
import os
import uuid
from collections import Counter
from pathlib import Path

from fastapi import UploadFile

from nutrack.config import settings
from nutrack.courses.catalog_parser import parse_catalog
from nutrack.courses.domain import CourseEntity
from nutrack.courses.exceptions import (
    CourseCatalogFileError,
    CourseGpaStatsFileError,
    CourseGpaStatsParsingError,
    CourseNotFoundError,
    CourseScheduleFileError,
    CourseScheduleParsingError,
    CourseSearchError,
)
from nutrack.courses.gpa_stats_parser import GpaStatEntry, parse_gpa_stats
from nutrack.courses.parser import parse_pdf_courses
from nutrack.courses.repository import CourseGpaStatsRepository, CourseOfferingRepository, CourseRepository
from nutrack.courses.schemas import (
    CourseCatalogUploadResponse,
    CourseDetailResponse,
    CourseSearchItem,
    CourseStatsResponse,
    GpaStatsUploadResponse,
    GradeCount,
    InvalidCatalogRow,
    InvalidGpaStatsRow,
)
from nutrack.semester import normalize_term

MAX_FILE_SIZE = 10 * 1024 * 1024
UPLOAD_DIR = Path("/tmp/schedule_uploads")
PDF_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}

logger = logging.getLogger(__name__)


CATALOG_FILE_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",  # .xls
    "text/csv",
    "application/csv",
    "application/octet-stream",
}
CATALOG_MAX_SIZE = 20 * 1024 * 1024  # 20 MB


def _canonical_payload(course: CourseEntity) -> dict[str, object]:
    return {
        "code": course.code,
        "level": course.level,
        "title": course.title,
        "department": course.department,
        "ects": course.ects,
        "description": course.description,
        "prerequisites": course.prerequisites,
        "pass_grade": course.pass_grade,
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
            raise CourseSearchError("term and year must both be provided together")
        try:
            return (normalize_term(term), year)
        except ValueError as exc:
            raise CourseSearchError(str(exc)) from exc


# ---------------------------------------------------------------------------
# CourseCatalogService
# ---------------------------------------------------------------------------


class CourseCatalogService:
    """
    Handles manual upload of the NU public course catalog (Excel/CSV).

    Distinct from CourseScheduleService (semester schedule PDF):
      - Schedule: which sections are offered this term, who teaches them.
      - Catalog: canonical course definitions (code, title, description,
        prerequisites, ECTS) that persist across semesters.
    """

    def __init__(
        self,
        course_repository: CourseRepository,
        gpa_stats_repository: CourseGpaStatsRepository,
    ) -> None:
        self.course_repository = course_repository
        self.gpa_stats_repository = gpa_stats_repository

    async def upload(self, file: UploadFile) -> CourseCatalogUploadResponse:
        payload, filename = await self._read_payload(file)
        try:
            entities, parse_errors = await asyncio.to_thread(
                parse_catalog, payload, filename
            )
        except ValueError as exc:
            raise CourseCatalogFileError(str(exc)) from exc

        inserted, updated, skipped = await self._upsert_all(entities)

        logger.info(
            "Course catalog upload completed.",
            extra={
                "filename": filename,
                "inserted": inserted,
                "updated": updated,
                "skipped": skipped,
                "parse_errors": len(parse_errors),
            },
        )

        return CourseCatalogUploadResponse(
            processed_rows=len(entities),
            inserted_count=inserted,
            updated_count=updated,
            skipped_count=skipped,
            invalid_rows_count=len(parse_errors),
            invalid_rows=[InvalidCatalogRow(**e) for e in parse_errors],
        )

    async def list_courses(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
    ) -> tuple[list[CourseDetailResponse], int]:
        courses, total = await asyncio.gather(
            self.course_repository.list_catalog(skip, limit, search),
            self.course_repository.count_catalog(search),
        )
        course_ids = [c.id for c in courses]
        gpa_map = await self.gpa_stats_repository.get_avg_gpa_by_course_ids(course_ids)
        result = []
        for c in courses:
            resp = CourseDetailResponse.model_validate(c)
            resp.avg_gpa = gpa_map.get(c.id)
            result.append(resp)
        return result, total

    async def get_course(self, course_id: int) -> CourseDetailResponse:
        course = await self.course_repository.get_by_id(course_id)
        if not course:
            raise CourseNotFoundError()
        resp = CourseDetailResponse.model_validate(course)
        gpa_map = await self.gpa_stats_repository.get_avg_gpa_by_course_ids([course_id])
        resp.avg_gpa = gpa_map.get(course_id)
        return resp

    # ------------------------------------------------------------------

    async def _read_payload(self, file: UploadFile) -> tuple[bytes, str]:
        filename = file.filename or ""
        content_type = (file.content_type or "").lower()
        name_lower = filename.lower()

        if not any(name_lower.endswith(ext) for ext in (".xlsx", ".xls", ".csv")):
            raise CourseCatalogFileError(
                "Only .xlsx, .xls, or .csv files are accepted for catalog upload."
            )
        if content_type and content_type not in CATALOG_FILE_TYPES:
            raise CourseCatalogFileError(
                f"Unexpected content type: {content_type}."
            )

        payload = await file.read()
        if not payload:
            raise CourseCatalogFileError("Uploaded file is empty.")
        if len(payload) > CATALOG_MAX_SIZE:
            raise CourseCatalogFileError("File exceeds 20 MB limit.")
        return payload, filename

    async def _upsert_all(
        self, entities: list[CourseEntity]
    ) -> tuple[int, int, int]:
        inserted = updated = skipped = 0
        for entity in entities:
            existing = await self.course_repository.get_by_code_and_level(
                entity.code, entity.level
            )
            payload = _canonical_payload(entity)
            if not existing:
                await self.course_repository.create(**payload)
                inserted += 1
            else:
                # Only update if at least one catalog field changed.
                changed = any(
                    getattr(existing, k) != v for k, v in payload.items()
                )
                if changed:
                    await self.course_repository.update(existing, **payload)
                    updated += 1
                else:
                    skipped += 1
        return inserted, updated, skipped


# ---------------------------------------------------------------------------
# CourseStatsService
# ---------------------------------------------------------------------------


class CourseStatsService:
    """
    Computes per-course aggregate statistics from the enrollments table.

    No separate stats table — queries are run live against enrollments.
    For high-traffic scenarios add a materialized view or a scheduled
    pre-computation job.
    """

    def __init__(self, course_repository: CourseRepository) -> None:
        self.course_repository = course_repository

    async def get_stats(self, course_id: int) -> CourseStatsResponse:
        course = await self.course_repository.get_by_id(course_id)
        if not course:
            raise CourseNotFoundError()

        agg = await self.course_repository.get_stats(course_id)
        grade_rows = await self.course_repository.get_grade_distribution(course_id)
        terms = await self.course_repository.get_terms_offered(course_id)

        total = agg["total_enrollments"] or 0
        passed = agg["passed_count"] or 0
        failed = agg["failed_count"] or 0
        withdrawn = agg["withdrawn_count"] or 0

        pass_rate: float | None = None
        withdraw_rate: float | None = None
        if total > 0:
            pass_rate = round(passed / total * 100, 1)
            withdraw_rate = round(withdrawn / total * 100, 1)

        grade_distribution = _build_grade_distribution(grade_rows, total)

        avg_gpa = agg["avg_gpa"]
        if avg_gpa is not None:
            avg_gpa = round(float(avg_gpa), 3)

        return CourseStatsResponse(
            course_id=course.id,
            code=course.code,
            level=course.level,
            title=course.title,
            total_enrollments=total,
            total_distinct_students=agg["total_distinct_students"] or 0,
            avg_gpa=avg_gpa,
            pass_rate=pass_rate,
            withdraw_rate=withdraw_rate,
            grade_distribution=grade_distribution,
            terms_offered=terms,
        )


def _build_grade_distribution(
    grade_rows: list[dict], total: int
) -> list[GradeCount]:
    if not grade_rows or total == 0:
        return []
    return [
        GradeCount(
            grade=row["grade"],
            count=row["count"],
            percentage=round(row["count"] / total * 100, 1),
        )
        for row in grade_rows
    ]


# ---------------------------------------------------------------------------
# CourseGpaStatsService
# ---------------------------------------------------------------------------

GPA_STATS_PDF_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
}
GPA_STATS_MAX_SIZE = 10 * 1024 * 1024  # 10 MB


class CourseGpaStatsService:
    """
    Handles manual upload of GPA statistics PDFs.

    One PDF covers a single semester (term + year).  Each row in the PDF
    maps to a (course_id, term, year, section) record in course_gpa_stats.
    """

    def __init__(
        self,
        course_repository: CourseRepository,
        gpa_stats_repository: CourseGpaStatsRepository,
    ) -> None:
        self.course_repository = course_repository
        self.gpa_stats_repository = gpa_stats_repository

    async def upload(
        self, file: UploadFile, term: str, year: int
    ) -> GpaStatsUploadResponse:
        normalized_term = normalize_term(term)
        payload, filename = await self._read_payload(file)

        try:
            entries, parse_errors = await asyncio.to_thread(
                parse_gpa_stats, payload, filename
            )
        except ValueError as exc:
            raise CourseGpaStatsParsingError(str(exc)) from exc

        inserted, updated = await self._upsert_all(entries, normalized_term, year)

        logger.info(
            "GPA stats upload completed.",
            extra={
                "filename": filename,
                "term": normalized_term,
                "year": year,
                "inserted": inserted,
                "updated": updated,
                "parse_errors": len(parse_errors),
            },
        )

        return GpaStatsUploadResponse(
            term=normalized_term,
            year=year,
            processed_rows=len(entries),
            inserted_count=inserted,
            updated_count=updated,
            invalid_rows_count=len(parse_errors),
            invalid_rows=[InvalidGpaStatsRow(**e) for e in parse_errors],
        )

    async def _read_payload(self, file: UploadFile) -> tuple[bytes, str]:
        filename = file.filename or ""
        content_type = (file.content_type or "").lower()

        if not filename.lower().endswith(".pdf"):
            raise CourseGpaStatsFileError("Only PDF files are accepted for GPA stats upload.")
        if content_type and content_type not in GPA_STATS_PDF_TYPES:
            raise CourseGpaStatsFileError(f"Unexpected content type: {content_type}.")

        payload = await file.read()
        if not payload:
            raise CourseGpaStatsFileError("Uploaded file is empty.")
        if len(payload) > GPA_STATS_MAX_SIZE:
            raise CourseGpaStatsFileError("File exceeds 10 MB limit.")
        return payload, filename

    async def _upsert_all(
        self, entries: list[GpaStatEntry], term: str, year: int
    ) -> tuple[int, int]:
        inserted = updated = 0
        for entry in entries:
            course = await self.course_repository.get_by_code_and_level(
                entry.code, entry.level
            )
            if not course:
                # Course not in catalog yet — skip silently; catalog must be uploaded first.
                logger.debug(
                    "GPA stats: course not found, skipping.",
                    extra={"code": entry.code, "level": entry.level},
                )
                continue

            existing = await self.gpa_stats_repository.get_by_identity(
                course.id, term, year, entry.section
            )
            payload = {
                "course_id": course.id,
                "term": term,
                "year": year,
                "section": entry.section,
                "avg_gpa": entry.avg_gpa,
                "total_enrolled": entry.total_enrolled,
                "grade_distribution": entry.grade_distribution or None,
            }
            if not existing:
                await self.gpa_stats_repository.create(**payload)
                inserted += 1
            else:
                await self.gpa_stats_repository.update(existing, **payload)
                updated += 1

        return inserted, updated
