from sqlalchemy import case, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.courses.models import Course, CourseGpaStats, CourseOffering
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.shared.db.base_repository import BaseRepository


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
    ) -> list[Course]:
        stmt = select(Course)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Course.code.ilike(pattern),
                    Course.title.ilike(pattern),
                    Course.department.ilike(pattern),
                )
            )
        stmt = stmt.order_by(Course.code, Course.level).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_catalog(self, search: str | None = None) -> int:
        stmt = select(func.count()).select_from(Course)
        if search:
            pattern = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Course.code.ilike(pattern),
                    Course.title.ilike(pattern),
                    Course.department.ilike(pattern),
                )
            )
        result = await self.session.execute(stmt)
        return result.scalar_one()

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
