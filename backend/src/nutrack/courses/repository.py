import re

from sqlalchemy import and_, case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.courses.models import Course, CourseGpaStats, CourseOffering
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.shared.db.base_repository import BaseRepository

# ---------------------------------------------------------------------------
# Section helpers
# ---------------------------------------------------------------------------

_RECITATION_TYPES = frozenset({"R", "LAB", "LB", "PLB", "TUT", "T"})


def _section_num(section: str | None) -> str:
    """Extract the leading numeric part of a section string.

    '1L' -> '1', '2S' -> '2', '1lab' -> '1', '2R' -> '2', '1' -> '1', None -> ''
    """
    if not section:
        return ""
    m = re.match(r"^(\d+)", section.strip())
    return m.group(1) if m else section.strip()


def _is_lecture_type(section: str | None) -> bool:
    """Return True when the section is a lecture/seminar (not a recitation or lab).

    NULL / numeric-only sections are treated as lecture type.
    """
    if not section:
        return True
    m = re.match(r"^\d+([A-Za-z]*)$", section.strip())
    if not m:
        return True
    type_part = m.group(1).upper()
    return type_part not in _RECITATION_TYPES


def _build_search_filter(pattern: str):
    combined_code = func.concat(Course.code, " ", Course.level)
    compact_code = func.concat(Course.code, Course.level)
    code_match = Course.code.ilike(pattern)
    combined_match = combined_code.ilike(pattern)
    compact_match = compact_code.ilike(pattern)
    level_match = Course.level.ilike(pattern)
    search_filter = or_(
        combined_match,
        compact_match,
        code_match,
        level_match,
        Course.title.ilike(pattern),
    )
    search_order = case(
        (combined_match, 0),
        (compact_match, 1),
        (code_match, 2),
        (level_match, 3),
        else_=4,
    )
    return search_filter, search_order


def _apply_catalog_filters(
    stmt, search, department, school, academic_level, term, level_prefix
):
    if search:
        raw = search.strip()
        pattern = f"%{raw}%"
        compact = raw.replace(" ", "")
        compact_pattern = f"%{compact}%"
        stmt = stmt.where(
            or_(
                Course.title.ilike(pattern),
                Course.department.ilike(pattern),
                # "MATH 161" — matches "code level" as a combined string
                func.concat(Course.code, " ", Course.level).ilike(pattern),
                # "MATH161" or "math161" — no-space variant
                func.concat(Course.code, Course.level).ilike(compact_pattern),
                # bare code match: "MATH"
                Course.code.ilike(pattern),
            )
        )
    if department:
        stmt = stmt.where(Course.department.ilike(f"%{department.strip()}%"))
    if school:
        stmt = stmt.where(Course.school.ilike(f"%{school.strip()}%"))
    if academic_level:
        stmt = stmt.where(Course.academic_level == academic_level)
    if term:
        subq = (
            select(CourseOffering.course_id)
            .where(CourseOffering.term == term)
            .distinct()
            .scalar_subquery()
        )
        stmt = stmt.where(Course.id.in_(subq))
    if level_prefix:
        # level_prefix is the leading digit: "1" filters 100-level, "2" for 200, etc.
        stmt = stmt.where(Course.level.like(f"{level_prefix}%"))
    return stmt


class CourseRepository(BaseRepository[Course]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Course)

    async def get_by_code_and_level(
        self,
        code: str,
        level: str,
    ) -> Course | None:
        stmt = (
            select(Course)
            .where(Course.code == code, Course.level == level)
            .order_by(Course.id)
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_catalog(
        self,
        skip: int = 0,
        limit: int = 20,
        search: str | None = None,
        department: str | None = None,
        school: str | None = None,
        academic_level: str | None = None,
        term: str | None = None,
        level_prefix: str | None = None,
    ) -> list[Course]:
        stmt = select(Course)
        stmt = _apply_catalog_filters(
            stmt, search, department, school, academic_level, term, level_prefix
        )
        stmt = stmt.order_by(Course.code, Course.level).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_catalog(
        self,
        search: str | None = None,
        department: str | None = None,
        school: str | None = None,
        academic_level: str | None = None,
        term: str | None = None,
        level_prefix: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(Course)
        stmt = _apply_catalog_filters(
            stmt, search, department, school, academic_level, term, level_prefix
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_terms_available_by_ids(
        self, course_ids: list[int]
    ) -> dict[int, list[str]]:
        """Bulk query: {course_id: sorted list of distinct term names}."""
        if not course_ids:
            return {}
        stmt = (
            select(CourseOffering.course_id, CourseOffering.term)
            .where(CourseOffering.course_id.in_(course_ids))
            .distinct()
        )
        result = await self.session.execute(stmt)
        out: dict[int, set[str]] = {}
        for row in result:
            out.setdefault(row.course_id, set()).add(row.term)
        return {k: sorted(v) for k, v in out.items()}

    async def get_stats(self, course_id: int) -> dict:
        """
        Aggregate enrollment statistics for a course across all offerings.

        Returns a dict with keys:
          total_enrollments, total_distinct_students,
          avg_gpa, passed_count, failed_count, withdrawn_count
        """
        stmt = (
            select(
                func.count(Enrollment.user_id).label("total_enrollments"),
                func.count(func.distinct(Enrollment.user_id)).label(
                    "total_distinct_students"
                ),
                func.avg(Enrollment.grade_points).label("avg_gpa"),
                func.count(
                    case(
                        (Enrollment.status == EnrollmentStatus.PASSED, 1),
                    )
                ).label("passed_count"),
                func.count(
                    case(
                        (Enrollment.status == EnrollmentStatus.FAILED, 1),
                    )
                ).label("failed_count"),
                func.count(
                    case(
                        (Enrollment.status == EnrollmentStatus.WITHDRAWN, 1),
                    )
                ).label("withdrawn_count"),
            )
            .select_from(Enrollment)
            .join(CourseOffering, Enrollment.course_id == CourseOffering.id)
            .where(CourseOffering.course_id == course_id)
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return dict(row)

    async def get_grade_distribution(
        self, course_id: int
    ) -> list[dict]:
        """Grade letter counts across all offerings of this course."""
        stmt = (
            select(
                Enrollment.grade,
                func.count(Enrollment.grade).label("count"),
            )
            .join(CourseOffering, Enrollment.course_id == CourseOffering.id)
            .where(
                CourseOffering.course_id == course_id,
                Enrollment.grade.is_not(None),
            )
            .group_by(Enrollment.grade)
            .order_by(func.count(Enrollment.grade).desc())
        )
        result = await self.session.execute(stmt)
        return [{"grade": row.grade, "count": row.count} for row in result]

    async def get_terms_offered(self, course_id: int) -> list[str]:
        """Sorted list of 'Term YYYY' strings for all offerings."""
        stmt = (
            select(CourseOffering.term, CourseOffering.year)
            .where(CourseOffering.course_id == course_id)
            .distinct()
            .order_by(CourseOffering.year, CourseOffering.term)
        )
        result = await self.session.execute(stmt)
        return [f"{row.term} {row.year}" for row in result]


class CourseOfferingRepository(BaseRepository[CourseOffering]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseOffering)

    async def get_by_identity(
        self,
        course_id: int,
        term: str,
        year: int,
        section: str | None,
    ) -> CourseOffering | None:
        stmt = select(CourseOffering).where(
            CourseOffering.course_id == course_id,
            CourseOffering.term == term,
            CourseOffering.year == year,
        )
        if section is None:
            stmt = stmt.where(CourseOffering.section.is_(None))
        else:
            stmt = stmt.where(CourseOffering.section == section)
        stmt = stmt.order_by(CourseOffering.id).limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def search(
        self,
        query: str | None,
        limit: int,
        term: str,
        year: int,
    ) -> list[CourseOffering]:
        stmt = (
            select(CourseOffering)
            .join(CourseOffering.course)
            .options(joinedload(CourseOffering.course))
            .where(
                CourseOffering.term == term,
                CourseOffering.year == year,
            )
        )
        cleaned = (query or "").strip()
        if cleaned:
            pattern = f"%{cleaned}%"
            search_filter, search_order = _build_search_filter(pattern)
            stmt = stmt.where(search_filter).order_by(search_order)
        stmt = stmt.order_by(
            Course.code,
            Course.level,
            Course.title,
            CourseOffering.section,
        )
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class CourseGpaStatsRepository(BaseRepository[CourseGpaStats]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CourseGpaStats)

    async def get_by_identity(
        self,
        course_id: int,
        term: str,
        year: int,
        section: str | None,
    ) -> CourseGpaStats | None:
        stmt = select(CourseGpaStats).where(
            CourseGpaStats.course_id == course_id,
            CourseGpaStats.term == term,
            CourseGpaStats.year == year,
        )
        if section is None:
            stmt = stmt.where(CourseGpaStats.section.is_(None))
        else:
            stmt = stmt.where(CourseGpaStats.section == section)
        stmt = stmt.limit(1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_avg_gpa_by_course_ids(
        self, course_ids: list[int]
    ) -> dict[int, float | None]:
        """Return {course_id: avg_gpa} averaged across all semesters."""
        if not course_ids:
            return {}
        stmt = (
            select(
                CourseGpaStats.course_id,
                func.avg(CourseGpaStats.avg_gpa).label("overall_avg_gpa"),
            )
            .where(
                CourseGpaStats.course_id.in_(course_ids),
                CourseGpaStats.avg_gpa.is_not(None),
            )
            .group_by(CourseGpaStats.course_id)
        )
        result = await self.session.execute(stmt)
        return {row.course_id: round(float(row.overall_avg_gpa), 3) for row in result}

    async def get_total_enrolled_by_course_ids(
        self, course_ids: list[int]
    ) -> dict[int, int]:
        """Sum enrolled from lecture/seminar offerings only (exclude labs/recitations).

        Recitations and labs share the same students as the lecture, so counting
        them would double-count.  We identify lecture-type sections in Python
        after fetching all (course_id, section, enrolled) rows.
        """
        if not course_ids:
            return {}
        stmt = (
            select(
                CourseOffering.course_id,
                CourseOffering.section,
                CourseOffering.enrolled,
            )
            .where(
                CourseOffering.course_id.in_(course_ids),
                CourseOffering.enrolled.is_not(None),
            )
        )
        result = await self.session.execute(stmt)
        totals: dict[int, int] = {}
        for row in result:
            if _is_lecture_type(row.section):
                totals[row.course_id] = totals.get(row.course_id, 0) + row.enrolled
        return totals

    async def get_sections_with_faculty(self, course_id: int) -> list[dict]:
        """Return GPA stats rows with faculty attached via Python-side matching.

        The GPA report stores section as a bare number ("1", "2") while the
        schedule stores it as "1L", "1R", "2S", "1lab", etc.  A plain SQL
        equality join would miss every match, so we fetch both tables and
        resolve faculty in Python by comparing just the leading numeric part.

        When multiple offerings share the same section number (e.g. "1L" and
        "1R"), we prefer the lecture/seminar row because that is where the
        faculty name appears in the schedule PDF.
        """
        # --- 1. Fetch GPA stats rows -----------------------------------------
        gpa_stmt = (
            select(
                CourseGpaStats.section,
                CourseGpaStats.term,
                CourseGpaStats.year,
                CourseGpaStats.avg_gpa,
                CourseGpaStats.total_enrolled,
                CourseGpaStats.grade_distribution,
            )
            .where(CourseGpaStats.course_id == course_id)
            .order_by(
                CourseGpaStats.year.desc(),
                CourseGpaStats.term,
                CourseGpaStats.section,
            )
        )
        gpa_result = await self.session.execute(gpa_stmt)
        rows = [dict(r._mapping) for r in gpa_result]
        if not rows:
            return []

        # --- 2. Fetch all offerings for this course --------------------------
        off_stmt = select(
            CourseOffering.term,
            CourseOffering.year,
            CourseOffering.section,
            CourseOffering.faculty,
        ).where(CourseOffering.course_id == course_id)
        off_result = await self.session.execute(off_stmt)

        # Build lookup: (term, year, section_num) -> faculty
        # If both lecture and recitation rows exist for the same section number,
        # the lecture row (is_lecture_type=True) wins.
        faculty_lookup: dict[tuple, str | None] = {}
        for o in off_result:
            key = (o.term, o.year, _section_num(o.section))
            is_lecture = _is_lecture_type(o.section)
            if key not in faculty_lookup or is_lecture:
                faculty_lookup[key] = o.faculty

        # --- 3. Attach faculty to each GPA stats row -------------------------
        for row in rows:
            key = (row["term"], row["year"], _section_num(row["section"]))
            row["faculty"] = faculty_lookup.get(key)

        return rows
