import asyncio
import logging
import os
import re
import uuid
from collections import Counter
from pathlib import Path

from fastapi import UploadFile

from nutrack.config import settings
from nutrack.courses.catalog_parser import parse_catalog
from nutrack.courses.domain import CourseEntity
from nutrack.courses.exceptions import (
    CourseCatalogFileError,
    CourseDescriptionsFileError,
    CourseGpaStatsFileError,
    CourseGpaStatsParsingError,
    CourseNotFoundError,
    CourseRequirementsFileError,
    CourseRequirementsParsingError,
    CourseScheduleFileError,
    CourseScheduleParsingError,
    CourseSearchError,
    ReviewAlreadyExistsError,
    ReviewForbiddenError,
    ReviewInappropriateContentError,
    ReviewNotFoundError,
)
from nutrack.courses.gpa_stats_parser import GpaStatEntry, parse_gpa_stats
from nutrack.courses.parser import parse_pdf_courses
from nutrack.courses.requirements_parser import parse_requirements
from nutrack.courses.profanity import contains_profanity
from nutrack.courses.repository import (
    CourseGpaStatsRepository,
    CourseOfferingRepository,
    CourseRepository,
    CourseReviewRepository,
)
from nutrack.courses.schemas import (
    AntirequisiteCheck,
    CourseCatalogUploadResponse,
    CorequisiteCheck,
    CourseDetailResponse,
    CourseOfferingInfo,
    CourseSearchItem,
    CourseStatsResponse,
    DescriptionsUploadResponse,
    EligibilityResponse,
    GpaStatsUploadResponse,
    GradeCount,
    InvalidCatalogRow,
    InvalidGpaStatsRow,
    PrerequisiteCheck,
    ProfessorStats,
    RequirementsUploadResponse,
    ReviewAuthor,
    ReviewCreate,
    ReviewResponse,
    ReviewStats,
    ReviewUpdate,
    ReviewsPage,
    SectionGpaStats,
)
from nutrack.enrollments.models import EnrollmentStatus
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
    # Deliberately excludes prerequisites/corequisites/antirequisites — those
    # are managed exclusively by the requirements upload and must not be
    # overwritten when the catalog or schedule is re-uploaded.
    return {
        "code": course.code,
        "level": course.level,
        "title": course.title,
        "department": course.department,
        "ects": course.ects,
        "description": course.description,
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


def _course_cols(course) -> dict:
    """Return only the loaded column values of a Course ORM object.

    Using __dict__ avoids triggering lazy-loads on relationships (e.g.
    `course.offerings`) which would fail outside an async greenlet context
    when Pydantic tries to read every field via from_attributes=True.
    """
    return {k: v for k, v in course.__dict__.items() if not k.startswith("_")}


_SCHOOL_MAJORS: dict[str, list[str]] = {
    "school of sciences and humanities": [
        # Declared majors (as they appear in priority texts and student profiles)
        "anthropology", "biological sciences", "biology", "chemistry",
        "economics", "history", "history and culture", "mathematics", "physics",
        "political science and international relations",
        "political sciences and international relations",
        "sociology",
        "world languages", "world languages, literatures and cultures",
        "literatures and cultures", "literature and culture",
        # Undeclared variants
        "undeclared ssh", "undeclared (ssh)",
    ],
    "school of engineering and digital sciences": [
        # Declared majors
        "chemical and materials engineering",
        "civil and environmental engineering",
        "computer science",
        "electrical and computer engineering",
        "mechanical and aerospace engineering",
        "robotics engineering", "robotics and mechatronics",
        # Undeclared variants
        "undeclared seds", "undeclared (seds)",
    ],
    "school of mining and geosciences": [
        "geology", "geosciences",
        "mining engineering",
        "petroleum engineering",
        # Undeclared variants
        "undeclared smg", "undeclared (smg)",
    ],
    "school of medicine": [
        "a six-year medical program", "medical sciences",
        "medicine", "nursing",
        # Undeclared variants
        "undeclared som", "undeclared nusom",
    ],
    "graduate school of business": [
        "business administration", "business administration (ug)",
        "undeclared gsb",
    ],
    "graduate school of education": [
        "education", "educational leadership",
        "undeclared gse",
    ],
    "graduate school of public policy": [
        "public policy", "public administration",
        "undeclared gspp",
    ],
}
# Abbreviation → canonical school name
_SCHOOL_ABBREV: dict[str, str] = {
    "ssh": "school of sciences and humanities",
    "seds": "school of engineering and digital sciences",
    "smg": "school of mining and geosciences",
    "som": "school of medicine",
    "nusom": "school of medicine",
    "gsb": "graduate school of business",
    "gse": "graduate school of education",
    "gspp": "graduate school of public policy",
}
# Pre-built: major (lower) → school name(s) it belongs to
_MAJOR_TO_SCHOOLS: dict[str, list[str]] = {}
for _school, _majors in _SCHOOL_MAJORS.items():
    for _m in _majors:
        _MAJOR_TO_SCHOOLS.setdefault(_m, []).append(_school)

# Matches "2 year UG SEDS" (all students in a school for that year, no specific major/qualifier)
_YEAR_SCHOOL_RE = re.compile(r"^\d+\s+year\s+ug\s+(\w+)$", re.IGNORECASE)


def _priority_text_matches(text: str, major_lower: str) -> bool:
    """Return True if priority text matches the user's major directly or via school.

    Priority text is a comma-separated list of items such as:
      "Computer Science", "SEDS", "2 year UG SEDS", "Undeclared SEDS"

    School-level matching (abbreviation) only fires when an item is the
    abbreviation alone ("SEDS") or a year+school without a specific major
    ("2 year UG SEDS").  Items like "Undeclared SEDS" are specific sub-groups
    and must NOT cause all SEDS students to match — only students whose major
    is literally "Undeclared SEDS" will match via the direct substring check.
    """
    text_lower = text.lower()
    # 1. Direct major substring match (handles specific majors AND "Undeclared SEDS" etc.)
    if major_lower in text_lower:
        return True

    # 2. School-level matching — only for items that represent the whole school
    schools_for_major = _MAJOR_TO_SCHOOLS.get(major_lower, [])
    if not schools_for_major:
        return False

    user_abbrevs = {
        abbrev
        for abbrev, canonical in _SCHOOL_ABBREV.items()
        if canonical in schools_for_major
    }
    user_school_names = set(schools_for_major)

    for raw_item in text.split(","):
        item = raw_item.strip().lower()
        # Exact school full name
        if item in user_school_names:
            return True
        # Exact abbreviation alone (e.g. item == "seds")
        if item in user_abbrevs:
            return True
        # "X year UG ABBREVIATION" with no further qualifier
        m = _YEAR_SCHOOL_RE.match(item)
        if m and m.group(1).lower() in user_abbrevs:
            return True

    return False


def _get_user_priority(course, user_major: str | None) -> int | None:
    """Return 1/2/3/4 if user's major (or their school) appears in that priority group text."""
    if not user_major:
        return None
    major_lower = user_major.lower()
    for level, text in [
        (1, course.priority_1),
        (2, course.priority_2),
        (3, course.priority_3),
        (4, course.priority_4),
    ]:
        if text and _priority_text_matches(text, major_lower):
            return level
    return None


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
        offering_repository: CourseOfferingRepository,
        review_repository: CourseReviewRepository,
    ) -> None:
        self.course_repository = course_repository
        self.gpa_stats_repository = gpa_stats_repository
        self.offering_repository = offering_repository
        self.review_repository = review_repository

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
        department: str | None = None,
        school: str | None = None,
        academic_level: str | None = None,
        term: str | None = None,
        level_prefix: str | None = None,
        eligible_only: bool = False,
        has_priority: bool = False,
        min_gpa: float | None = None,
        min_rating: float | None = None,
        user_id: int | None = None,
        user_major: str | None = None,
        kazakh_level: str | None = None,
    ) -> tuple[list[CourseDetailResponse], int]:
        # When filtering by eligibility, priority, GPA, or rating (all Python-computed),
        # fetch all matching rows from DB, apply filters, then paginate manually.
        needs_post_filter = (
            (eligible_only or has_priority) and user_id is not None
        ) or min_gpa is not None or min_rating is not None
        if needs_post_filter:
            courses = await self.course_repository.list_catalog(
                0, 10_000, search, department, school, academic_level, term, level_prefix
            )
        else:
            courses, _ = await asyncio.gather(
                self.course_repository.list_catalog(
                    skip, limit, search, department, school, academic_level, term, level_prefix
                ),
                # total computed below
                asyncio.sleep(0),
            )

        total_unfiltered = await self.course_repository.count_catalog(
            search, department, school, academic_level, term, level_prefix
        )

        course_ids = [c.id for c in courses]
        gpa_map, enrolled_map, terms_map, offerings_map, rating_map = await asyncio.gather(
            self.gpa_stats_repository.get_avg_gpa_by_course_ids(course_ids),
            self.gpa_stats_repository.get_total_enrolled_by_course_ids(course_ids),
            self.course_repository.get_terms_available_by_ids(course_ids),
            self.offering_repository.get_latest_offerings_batch(course_ids),
            self.review_repository.get_avg_overall_rating_by_course_ids(course_ids),
        )

        # Fetch user enrollment history once for eligibility computation
        history: list[dict] = []
        passed: dict[int, dict] = {}
        in_progress: set[int] = set()
        code_to_id: dict[tuple[str, str], int] = {}
        if user_id is not None:
            history = await self.course_repository.get_user_course_history(user_id)
            passed = {
                r["id"]: r
                for r in history
                if r["status"] == EnrollmentStatus.PASSED
            }
            in_progress = {
                r["id"]
                for r in history
                if r["status"] == EnrollmentStatus.IN_PROGRESS
            }
            # Batch-resolve all prerequisite course codes to catalog IDs.
            all_pairs = _collect_req_pairs(
                *[text for c in courses for text in (c.prerequisites, c.corequisites, c.antirequisites)]
            )
            code_to_id = await self.course_repository.get_ids_by_code_levels(all_pairs)

        result = []
        for c in courses:
            resp = CourseDetailResponse.model_validate(_course_cols(c))
            resp.avg_gpa = gpa_map.get(c.id)
            resp.total_enrolled = enrolled_map.get(c.id)
            resp.terms_available = terms_map.get(c.id, [])
            resp.avg_review_rating = rating_map.get(c.id)
            resp.offerings = [
                CourseOfferingInfo(
                    section=o.section,
                    faculty=re.sub(r"\s+", " ", o.faculty or "").strip() or None,
                    meeting_time=o.meeting_time,
                    room=o.room,
                    days=o.days,
                    enrolled=o.enrolled,
                    capacity=o.capacity,
                    term=o.term,
                    year=o.year,
                )
                for o in offerings_map.get(c.id, [])
            ]

            if user_id is not None:
                prereq_checks, prereqs_met = (
                    _build_prereq_checks(c.prerequisites, passed, code_to_id, kazakh_level)
                    if c.prerequisites
                    else ([], True)
                )
                coreq_checks, coreqs_met = (
                    _build_coreq_checks(c.corequisites, passed, in_progress, code_to_id)
                    if c.corequisites
                    else ([], True)
                )
                antireq_checks, antireqs_blocking = (
                    _build_antireq_checks(c.antirequisites, passed, code_to_id)
                    if c.antirequisites
                    else ([], False)
                )
                enrollment = passed.get(c.id)
                already_taken = enrollment is not None and enrollment.get("grade") != "F"
                resp.is_eligible = prereqs_met and coreqs_met and not antireqs_blocking and not already_taken
                if not resp.is_eligible:
                    resp.ineligibility_reason = _ineligibility_reason(
                        prereqs_met, coreqs_met, antireqs_blocking, already_taken,
                        prereq_checks, coreq_checks, antireq_checks,
                    )
                resp.user_priority = _get_user_priority(c, user_major)

            result.append(resp)

        if needs_post_filter:
            if eligible_only:
                result = [r for r in result if r.is_eligible is True]
            if has_priority:
                result = [r for r in result if r.user_priority is not None]
            if min_gpa is not None:
                result = [r for r in result if r.avg_gpa is not None and r.avg_gpa >= min_gpa]
            if min_rating is not None:
                result = [r for r in result if r.avg_review_rating is not None and r.avg_review_rating >= min_rating]
            total = len(result)
            result = result[skip : skip + limit]
        else:
            total = total_unfiltered

        return result, total

    async def get_course(self, course_id: int) -> CourseDetailResponse:
        course = await self.course_repository.get_by_id(course_id)
        if not course:
            raise CourseNotFoundError()
        resp = CourseDetailResponse.model_validate(_course_cols(course))
        gpa_map, enrolled_map, terms_map, section_rows, latest_offerings, rating_map = await asyncio.gather(
            self.gpa_stats_repository.get_avg_gpa_by_course_ids([course_id]),
            self.gpa_stats_repository.get_total_enrolled_by_course_ids([course_id]),
            self.course_repository.get_terms_available_by_ids([course_id]),
            self.gpa_stats_repository.get_sections_with_faculty(course_id),
            self.offering_repository.get_latest_offerings(course_id),
            self.review_repository.get_avg_overall_rating_by_course_ids([course_id]),
        )
        resp.avg_gpa = gpa_map.get(course_id)
        resp.total_enrolled = enrolled_map.get(course_id)
        resp.terms_available = terms_map.get(course_id, [])
        resp.avg_review_rating = rating_map.get(course_id)
        resp.sections = [
            SectionGpaStats(
                section=row["section"],
                term=row["term"],
                year=row["year"],
                faculty=row["faculty"],
                avg_gpa=row["avg_gpa"],
                total_enrolled=row["total_enrolled"],
                grade_distribution=row["grade_distribution"] or {},
            )
            for row in section_rows
        ]
        resp.professors = _group_by_professor(resp.sections)
        resp.offerings = [
            CourseOfferingInfo(
                section=o.section,
                faculty=re.sub(r"\s+", " ", o.faculty or "").strip() or None,
                meeting_time=o.meeting_time,
                room=o.room,
                days=o.days,
                enrolled=o.enrolled,
                capacity=o.capacity,
                term=o.term,
                year=o.year,
            )
            for o in latest_offerings
        ]
        return resp

    # ------------------------------------------------------------------

    async def upload_descriptions(self, file: UploadFile) -> DescriptionsUploadResponse:
        """
        Accept a JSON file (array of {code, level, description}) and bulk-update
        course descriptions.  Rows with empty description are skipped.
        Only courses already in the catalog are updated.
        """
        import json as _json

        filename = file.filename or ""
        if not filename.lower().endswith(".json"):
            raise CourseDescriptionsFileError("Only .json files are accepted.")

        payload = await file.read()
        if not payload:
            raise CourseDescriptionsFileError("Uploaded file is empty.")
        if len(payload) > 10 * 1024 * 1024:
            raise CourseDescriptionsFileError("File exceeds 10 MB limit.")

        try:
            entries = _json.loads(payload)
        except _json.JSONDecodeError as exc:
            raise CourseDescriptionsFileError(f"Invalid JSON: {exc}") from exc

        if not isinstance(entries, list):
            raise CourseDescriptionsFileError("JSON must be an array of course objects.")

        updated = skipped_empty = skipped_unchanged = not_found = 0

        for entry in entries:
            if not isinstance(entry, dict):
                continue
            code = str(entry.get("code") or "").strip()
            level = str(entry.get("level") or "").strip()
            description = str(entry.get("description") or "").strip()

            if not description:
                skipped_empty += 1
                continue

            course = await self.course_repository.get_by_code_and_level(code, level)
            if not course:
                not_found += 1
                continue

            if course.description == description:
                skipped_unchanged += 1
                continue

            await self.course_repository.update(course, description=description)
            updated += 1

        logger.info(
            "Descriptions upload completed.",
            extra={
                "filename": filename,
                "updated": updated,
                "skipped_empty": skipped_empty,
                "skipped_unchanged": skipped_unchanged,
                "not_found": not_found,
            },
        )
        return DescriptionsUploadResponse(
            processed_rows=len(entries),
            updated_count=updated,
            skipped_empty=skipped_empty,
            skipped_unchanged=skipped_unchanged,
            not_found_count=not_found,
        )

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


def _group_by_professor(sections: list[SectionGpaStats]) -> list[ProfessorStats]:
    """Group section GPA stats by faculty name, compute per-professor avg GPA.

    Sections without a resolved faculty are skipped — they will still appear
    in the overall grade distribution but won't create a phantom "Unknown" entry.
    When a section is co-taught (faculty = "Prof A, Prof B"), it is attributed
    to each professor individually so their stats remain separate.
    """
    grouped: dict[str, list[SectionGpaStats]] = {}
    for s in sections:
        if not s.faculty:
            continue
        # Split co-taught sections by comma separator
        names = [name.strip() for name in s.faculty.split(",") if name.strip()]
        for name in names:
            grouped.setdefault(name, []).append(s)
    result = []
    for faculty, sec_list in grouped.items():
        gpas = [s.avg_gpa for s in sec_list if s.avg_gpa is not None]
        avg = round(sum(gpas) / len(gpas), 3) if gpas else None
        total = sum(s.total_enrolled for s in sec_list if s.total_enrolled is not None)
        result.append(
            ProfessorStats(
                faculty=faculty,
                sections=sec_list,
                avg_gpa=avg,
                total_enrolled=total,
            )
        )
    result.sort(key=lambda p: (p.avg_gpa is None, -(p.avg_gpa or 0)))
    return result


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
                # Course not in catalog yet — skip; catalog must be uploaded first.
                logger.warning(
                    "GPA stats: course not found in catalog, skipping.",
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


# ---------------------------------------------------------------------------
# CourseReviewService
# ---------------------------------------------------------------------------


def _review_to_response(review) -> ReviewResponse:
    return ReviewResponse(
        id=review.id,
        course_id=review.course_id,
        user_id=review.user_id,
        author=ReviewAuthor(
            id=review.user.id,
            first_name=review.user.first_name,
            last_name=review.user.last_name,
        ),
        comment=review.comment,
        overall_rating=review.overall_rating,
        difficulty=review.difficulty,
        informativeness=review.informativeness,
        gpa_boost=review.gpa_boost,
        workload=review.workload,
        created_at=review.created_at,
        updated_at=review.updated_at,
    )


class CourseReviewService:
    def __init__(
        self,
        course_repository: CourseRepository,
        review_repository: CourseReviewRepository,
    ) -> None:
        self.course_repository = course_repository
        self.review_repository = review_repository

    async def list_reviews(
        self,
        course_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> ReviewsPage:
        course = await self.course_repository.get_by_id(course_id)
        if not course:
            raise CourseNotFoundError()

        reviews, total, avg_ratings = await asyncio.gather(
            self.review_repository.get_by_course(course_id, skip, limit),
            self.review_repository.count_by_course(course_id),
            self.review_repository.get_avg_ratings(course_id),
        )
        return ReviewsPage(
            stats=ReviewStats(total=total, **avg_ratings),
            reviews=[_review_to_response(r) for r in reviews],
        )

    async def create_review(
        self,
        course_id: int,
        user_id: int,
        data: ReviewCreate,
    ) -> ReviewResponse:
        course = await self.course_repository.get_by_id(course_id)
        if not course:
            raise CourseNotFoundError()

        existing = await self.review_repository.get_by_user_and_course(user_id, course_id)
        if existing:
            raise ReviewAlreadyExistsError()

        if data.comment and contains_profanity(data.comment):
            raise ReviewInappropriateContentError()

        review = await self.review_repository.create(
            course_id=course_id,
            user_id=user_id,
            comment=data.comment,
            overall_rating=data.overall_rating,
            difficulty=data.difficulty,
            informativeness=data.informativeness,
            gpa_boost=data.gpa_boost,
            workload=data.workload,
        )
        # Re-fetch to load user relationship
        review = await self.review_repository.get_by_id_with_user(review.id)
        return _review_to_response(review)

    async def update_review(
        self,
        course_id: int,
        review_id: int,
        user_id: int,
        data: ReviewUpdate,
    ) -> ReviewResponse:
        review = await self.review_repository.get_by_id_with_user(review_id)
        if not review or review.course_id != course_id:
            raise ReviewNotFoundError()
        if review.user_id != user_id:
            raise ReviewForbiddenError()

        if data.comment and contains_profanity(data.comment):
            raise ReviewInappropriateContentError()

        updates = {k: v for k, v in data.model_dump().items() if v is not None}
        review = await self.review_repository.update(review, **updates)
        # Re-fetch to get updated timestamps with loaded user
        review = await self.review_repository.get_by_id_with_user(review.id)
        return _review_to_response(review)

    async def delete_review(
        self,
        course_id: int,
        review_id: int,
        user_id: int,
    ) -> None:
        review = await self.review_repository.get_by_id_with_user(review_id)
        if not review or review.course_id != course_id:
            raise ReviewNotFoundError()
        if review.user_id != user_id:
            raise ReviewForbiddenError()
        await self.review_repository.delete(review)


# ---------------------------------------------------------------------------
# CourseRequirementsService
# ---------------------------------------------------------------------------

REQUIREMENTS_MAX_SIZE = 10 * 1024 * 1024  # 10 MB


_TERM_PRIORITY = {"Spring": 2, "Summer": 1, "Fall": 0}


def _req_score(term: str, year: int) -> int:
    """Higher score = higher priority. Spring beats Fall within the same year."""
    return year * 10 + _TERM_PRIORITY.get(term, 0)


class CourseRequirementsService:
    """Upload Course Requirements PDF to update prerequisites/corequisites."""

    def __init__(self, course_repository: CourseRepository) -> None:
        self.course_repository = course_repository

    async def upload(self, file: UploadFile, term: str, year: int) -> RequirementsUploadResponse:
        normalized_term = normalize_term(term)
        new_score = _req_score(normalized_term, year)
        payload, filename = await self._read_payload(file)
        try:
            entries, errors = await asyncio.to_thread(
                parse_requirements, payload, filename
            )
        except ValueError as exc:
            raise CourseRequirementsParsingError(str(exc)) from exc

        updated = not_found = skipped = lower_priority = 0
        for entry in entries:
            course = await self.course_repository.get_by_code_and_level(
                entry.code, entry.level
            )
            if not course:
                not_found += 1
                continue

            # Skip if the course already has higher-priority semester data
            if course.requirements_term and course.requirements_year is not None:
                existing_score = _req_score(course.requirements_term, course.requirements_year)
                if new_score < existing_score:
                    lower_priority += 1
                    continue

            changed = (
                course.prerequisites != entry.prerequisites
                or course.corequisites != entry.corequisites
                or course.antirequisites != entry.antirequisites
                or course.priority_1 != entry.priority_1
                or course.priority_2 != entry.priority_2
                or course.priority_3 != entry.priority_3
                or course.priority_4 != entry.priority_4
                or course.requirements_term != normalized_term
                or course.requirements_year != year
            )
            if changed:
                await self.course_repository.update(
                    course,
                    prerequisites=entry.prerequisites,
                    corequisites=entry.corequisites,
                    antirequisites=entry.antirequisites,
                    priority_1=entry.priority_1,
                    priority_2=entry.priority_2,
                    priority_3=entry.priority_3,
                    priority_4=entry.priority_4,
                    requirements_term=normalized_term,
                    requirements_year=year,
                )
                updated += 1
            else:
                skipped += 1

        logger.info(
            "Requirements upload completed.",
            extra={
                "filename": filename,
                "term": normalized_term,
                "year": year,
                "processed_rows": len(entries),
                "updated": updated,
                "not_found": not_found,
                "skipped": skipped,
                "lower_priority": lower_priority,
                "parse_errors": len(errors),
            },
        )
        return RequirementsUploadResponse(
            processed_rows=len(entries),
            updated_count=updated,
            not_found_count=not_found,
            skipped_count=skipped,
            lower_priority_count=lower_priority,
            error_count=len(errors),
        )

    async def _read_payload(self, file: UploadFile) -> tuple[bytes, str]:
        filename = file.filename or ""
        content_type = (file.content_type or "").lower()
        if not filename.lower().endswith(".pdf"):
            raise CourseRequirementsFileError("Only PDF files are accepted.")
        if content_type and content_type not in PDF_TYPES:
            raise CourseRequirementsFileError(
                f"Unexpected content type: {content_type}."
            )
        payload = await file.read()
        if not payload:
            raise CourseRequirementsFileError("Uploaded file is empty.")
        if len(payload) > REQUIREMENTS_MAX_SIZE:
            raise CourseRequirementsFileError("File exceeds 10 MB limit.")
        return payload, filename


# ---------------------------------------------------------------------------
# CourseEligibilityService — helpers
# ---------------------------------------------------------------------------

_COURSE_RE = re.compile(r"\b([A-Z]{2,6})\s+(\d{2,4}[A-Za-z]?)\b")

KLL_LEVEL_ORDER = ["A1", "A2", "B1", "B2", "C1", "C2"]

# Matches the actual DB format: KLL "[B1.2] Intermediate" / KLL "[C1.1] Advanced"
_KLL_PREREQ_RE = re.compile(r"\bKLL\b[^[]*\[([A-C][12])\.\d\]", re.IGNORECASE)

_GRADE_REQ_RE = re.compile(r"\(([A-F][+-]?)\s+and\s+above\)", re.IGNORECASE)
_HAS_OR_RE = re.compile(r"\bor\b", re.IGNORECASE)

_GRADE_POINTS_MAP: dict[str, float] = {
    "A": 4.0,
    "A-": 3.67,
    "B+": 3.33,
    "B": 3.0,
    "B-": 2.67,
    "C+": 2.33,
    "C": 2.0,
    "C-": 1.67,
    "D+": 1.33,
    "D": 1.0,
    "F": 0.0,
}


def _ineligibility_reason(
    prereqs_met: bool,
    coreqs_met: bool,
    antireqs_blocking: bool,
    already_taken: bool,
    prereq_checks: list,
    coreq_checks: list,
    antireq_checks: list,
) -> str | None:
    if already_taken:
        return "Already completed"
    parts: list[str] = []
    if not prereqs_met:
        missing = [c.course_code for c in prereq_checks if not c.met]
        parts.append(
            f"Prerequisites not met: {', '.join(missing)}" if missing else "Prerequisites not met"
        )
    if not coreqs_met:
        missing = [c.course_code for c in coreq_checks if not c.met]
        parts.append(
            f"Corequisites not met: {', '.join(missing)}" if missing else "Corequisites not met"
        )
    if antireqs_blocking:
        blocking = [c.course_code for c in antireq_checks if c.blocking]
        parts.append(
            f"Already took: {', '.join(blocking)}" if blocking else "Antirequisite conflict"
        )
    return "; ".join(parts) if parts else None


def _build_kll_check(text: str, kazakh_level: str | None) -> "PrerequisiteCheck | None":
    """Return a PrerequisiteCheck for a KLL requirement if present in text, else None."""
    m = _KLL_PREREQ_RE.search(text)
    if not m:
        return None
    required = m.group(1).upper()  # e.g. "B1", "C1"
    if kazakh_level:
        try:
            met = KLL_LEVEL_ORDER.index(kazakh_level.upper()) >= KLL_LEVEL_ORDER.index(required)
        except ValueError:
            met = False
    else:
        met = False
    return PrerequisiteCheck(
        course_code=f"KLL {required}",
        met=met,
        your_grade=f"KLL {kazakh_level}" if met else None,
    )


def _collect_req_pairs(*texts: str | None) -> list[tuple[str, str]]:
    """Extract unique (code, level) pairs from one or more requirement text fields."""
    seen: set[tuple[str, str]] = set()
    for text in texts:
        if text:
            for code, level in _COURSE_RE.findall(text):
                seen.add((code.upper(), level))
    return list(seen)


def _build_prereq_checks(
    text: str,
    passed: dict[int, dict],
    code_to_id: dict[tuple[str, str], int],
    kazakh_level: str | None = None,
) -> tuple[list[PrerequisiteCheck], bool]:
    """Parse prerequisite text and check against passed enrollments.

    Returns (checks, overall_met).  OR logic applies when "or" appears in text.
    KLL "[X1.Y] ..." patterns are checked against the user's kazakh_level.
    """
    has_or = bool(_HAS_OR_RE.search(text))
    grade_match = _GRADE_REQ_RE.search(text)
    global_grade = grade_match.group(1).upper() if grade_match else None

    courses = _COURSE_RE.findall(text)
    kll_check = _build_kll_check(text, kazakh_level)

    if not courses and kll_check is None:
        return [], True

    checks: list[PrerequisiteCheck] = []
    for code, level in courses:
        course_id = code_to_id.get((code.upper(), level))
        enrollment = passed.get(course_id) if course_id is not None else None
        if enrollment is None:
            checks.append(
                PrerequisiteCheck(
                    course_code=f"{code} {level}",
                    required_grade=global_grade,
                    met=False,
                    your_grade=None,
                )
            )
            continue
        if global_grade:
            req_pts = _GRADE_POINTS_MAP.get(global_grade, 0.0)
            your_pts = float(enrollment.get("grade_points") or 0.0)
            met = your_pts >= req_pts
        else:
            met = True
        checks.append(
            PrerequisiteCheck(
                course_code=f"{code} {level}",
                required_grade=global_grade,
                met=met,
                your_grade=enrollment.get("grade"),
            )
        )

    if kll_check is not None:
        checks.append(kll_check)

    if not checks:
        return [], True

    overall = any(c.met for c in checks) if has_or else all(c.met for c in checks)
    return checks, overall


def _build_coreq_checks(
    text: str,
    passed: dict[int, dict],
    in_progress: set[int],
    code_to_id: dict[tuple[str, str], int],
) -> tuple[list[CorequisiteCheck], bool]:
    """Parse corequisite text and check against passed/in-progress enrollments.

    Returns (checks, overall_met).  OR logic applies when "or" appears in text.
    """
    has_or = bool(_HAS_OR_RE.search(text))
    courses = _COURSE_RE.findall(text)
    if not courses:
        return [], True

    checks: list[CorequisiteCheck] = []
    for code, level in courses:
        course_id = code_to_id.get((code.upper(), level))
        passed_info = passed.get(course_id) if course_id is not None else None
        in_prog = course_id in in_progress if course_id is not None else False
        if passed_info:
            checks.append(
                CorequisiteCheck(
                    course_code=f"{code} {level}",
                    met=True,
                    your_grade=passed_info.get("grade"),
                    your_status="passed",
                )
            )
        elif in_prog:
            checks.append(
                CorequisiteCheck(
                    course_code=f"{code} {level}",
                    met=True,
                    your_grade=None,
                    your_status="in_progress",
                )
            )
        else:
            checks.append(
                CorequisiteCheck(
                    course_code=f"{code} {level}",
                    met=False,
                    your_grade=None,
                    your_status=None,
                )
            )

    overall = any(c.met for c in checks) if has_or else all(c.met for c in checks)
    return checks, overall


def _build_antireq_checks(
    text: str,
    passed: dict[int, dict],
    code_to_id: dict[tuple[str, str], int],
) -> tuple[list[AntirequisiteCheck], bool]:
    """Parse antirequisite text and check if user has already taken any of them.

    Returns (checks, is_blocking). If the user has passed ANY antirequisite,
    is_blocking = True and they cannot register.
    """
    courses = _COURSE_RE.findall(text)
    if not courses:
        return [], False

    checks: list[AntirequisiteCheck] = []
    for code, level in courses:
        course_id = code_to_id.get((code.upper(), level))
        enrollment = passed.get(course_id) if course_id is not None else None
        if enrollment:
            checks.append(
                AntirequisiteCheck(
                    course_code=f"{code} {level}",
                    blocking=True,
                    your_grade=enrollment.get("grade"),
                )
            )
        else:
            checks.append(
                AntirequisiteCheck(
                    course_code=f"{code} {level}",
                    blocking=False,
                    your_grade=None,
                )
            )

    is_blocking = any(c.blocking for c in checks)
    return checks, is_blocking


class CourseEligibilityService:
    """Check whether a user is eligible to register for a course."""

    def __init__(self, course_repository: CourseRepository) -> None:
        self.course_repository = course_repository

    async def check_eligibility(
        self, course_id: int, user_id: int, kazakh_level: str | None = None
    ) -> EligibilityResponse:
        course = await self.course_repository.get_by_id(course_id)
        if not course:
            raise CourseNotFoundError()

        history = await self.course_repository.get_user_course_history(user_id)

        passed: dict[int, dict] = {
            r["id"]: r
            for r in history
            if r["status"] == EnrollmentStatus.PASSED
        }
        in_progress: set[int] = {
            r["id"]
            for r in history
            if r["status"] == EnrollmentStatus.IN_PROGRESS
        }

        all_pairs = _collect_req_pairs(
            course.prerequisites, course.corequisites, course.antirequisites
        )
        code_to_id = await self.course_repository.get_ids_by_code_levels(all_pairs)

        prereq_checks, prereqs_met = (
            _build_prereq_checks(course.prerequisites, passed, code_to_id, kazakh_level)
            if course.prerequisites
            else ([], True)
        )
        coreq_checks, coreqs_met = (
            _build_coreq_checks(course.corequisites, passed, in_progress, code_to_id)
            if course.corequisites
            else ([], True)
        )
        antireq_checks, antireqs_blocking = (
            _build_antireq_checks(course.antirequisites, passed, code_to_id)
            if course.antirequisites
            else ([], False)
        )

        enrollment = passed.get(course_id)
        already_taken = enrollment is not None and enrollment.get("grade") != "F"
        return EligibilityResponse(
            course_id=course_id,
            can_register=prereqs_met and coreqs_met and not antireqs_blocking and not already_taken,
            prerequisites_met=prereqs_met,
            corequisites_met=coreqs_met,
            antirequisites_blocking=antireqs_blocking,
            prerequisite_checks=prereq_checks,
            corequisite_checks=coreq_checks,
            antirequisite_checks=antireq_checks,
        )
