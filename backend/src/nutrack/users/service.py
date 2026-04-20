from sqlalchemy import select
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, load_only

from nutrack.courses.models import Course, CourseOffering
from nutrack.courses.repository import CourseRepository
from nutrack.courses.service import _get_user_priority, _COURSE_RE, _GRADE_REQ_RE, _GRADE_POINTS_MAP
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.enrollments.service import EnrollmentService, format_course_code
from nutrack.config import settings
from nutrack.handbook.service import HandbookService
from nutrack.users.audit import compute_audit, get_terms_for_patterns
from nutrack.users.exceptions import NotFoundError
from nutrack.users.repository import UserRepository
from nutrack.users.schemas import (
    AuditResultResponse,
    CategoryResultResponse,
    CreditsBySemester,
    DegreePlanResponse,
    EnrollmentResponse,
    MatchedCourseResponse,
    PlannedCourseResponse,
    PlannedTermResponse,
    RequirementResultResponse,
    SuggestedCourseResponse,
    UserProfileResponse,
    UserProfileUpdate,
    UserStatsResponse,
)
from nutrack.semester import format_term_year as _fmt_term_year
from nutrack.users.utils import term_year_sort_key

_TERM_CAPACITY = {"Spring": 5, "Fall": 5, "Summer": 2}
_TERM_NEXT: dict[str, tuple[str, int]] = {
    "Spring": ("Summer", 0),
    "Summer": ("Fall", 0),
    "Fall": ("Spring", 1),
}


def _generate_future_terms(current_term: str, current_year: int, max_terms: int = 25) -> list[tuple[str, int]]:
    """Generate future terms (Spring/Summer/Fall) after the current one."""
    terms: list[tuple[str, int]] = []
    t, y = current_term, current_year
    for _ in range(max_terms):
        next_t, dy = _TERM_NEXT[t]
        t, y = next_t, y + dy
        terms.append((t, y))
    return terms


def _study_year_at_term(enrollment_year: int | None, term: str, year: int) -> int | None:
    """Return the student's year of study (1-based) at a given future term."""
    if not enrollment_year:
        return None
    if term == "Fall":
        return year - enrollment_year + 1
    else:  # Spring or Summer
        return year - enrollment_year



def course_loader():
    return joinedload(Enrollment.course_offering).options(
        load_only(CourseOffering.id, CourseOffering.course_id),
        joinedload(CourseOffering.course).load_only(
            Course.id,
            Course.code,
            Course.level,
            Course.title,
            Course.ects,
        ),
    )


def _is_missing_handbook_table(error: ProgrammingError) -> bool:
    return 'relation "handbook_plans" does not exist' in str(error)


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_profile(self, user_id: int) -> UserProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")
        return UserProfileResponse.model_validate(user)

    async def update_profile(
        self,
        user_id: int,
        data: UserProfileUpdate,
    ) -> UserProfileResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            await self.user_repo.update(user, **update_data)

        return UserProfileResponse.model_validate(user)

    async def get_enrollments(self, user_id: int) -> list[EnrollmentResponse]:
        service = EnrollmentService(self.session)
        return await service.list_enrollments(user_id)

    async def get_stats(self, user_id: int) -> UserStatsResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        stmt = (
            select(Enrollment)
            .options(course_loader())
            .where(Enrollment.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        enrollments = list(result.scalars().unique().all())

        total_credits = user.total_credits_earned or 0
        completed_courses = len(
            [e for e in enrollments if e.status == EnrollmentStatus.PASSED]
        )
        semesters = {(e.term, e.year) for e in enrollments}

        credits_map: dict[tuple[str, int], int] = {}
        for enrollment in enrollments:
            key = (enrollment.term, enrollment.year)
            credits_map[key] = (
                credits_map.get(key, 0)
                + enrollment.course_offering.course.ects
            )

        credits_by_semester = [
            CreditsBySemester(
                semester=format_term_year(term, year),
                term=term,
                year=year,
                credits=credits,
            )
            for (term, year), credits in sorted(
                credits_map.items(),
                key=lambda item: term_year_sort_key(item[0][0], item[0][1]),
            )
        ]

        return UserStatsResponse(
            total_credits=total_credits,
            completed_courses=completed_courses,
            current_gpa=user.cgpa,
            semesters_completed=len(semesters),
            credits_by_semester=credits_by_semester,
        )

    async def get_audit(self, user_id: int) -> AuditResultResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        major = (user.major or "").strip()

        stmt = (
            select(Enrollment)
            .options(course_loader())
            .where(Enrollment.user_id == user_id)
            .where(
                Enrollment.status.in_(
                    [EnrollmentStatus.PASSED, EnrollmentStatus.IN_PROGRESS]
                )
            )
        )
        result = await self.session.execute(stmt)
        enrollments = list(result.scalars().unique().all())

        courses: list[tuple[str, str]] = []
        for e in enrollments:
            code = format_course_code(
                e.course_offering.course.code,
                e.course_offering.course.level,
            )
            courses.append((code, e.status.value))

        # Derive enrollment year from study_year: e.g. 4th year in 2026 → enrolled 2022
        enrollment_year = (
            settings.CURRENT_YEAR - user.study_year
            if user.study_year
            else None
        )

        # Load handbook plans for this enrollment year if available
        handbook_plans = None
        if enrollment_year:
            handbook_svc = HandbookService(self.session)
            try:
                handbook_plans = await handbook_svc.get_plans_for_year(
                    enrollment_year
                )
            except ProgrammingError as exc:
                if not _is_missing_handbook_table(exc):
                    raise

        audit = compute_audit(major, courses, user.total_credits_earned or 0, handbook_plans, kazakh_level=user.kazakh_level)

        # Fetch all course-term pairs once; used to resolve term availability for
        # each requirement so the frontend can factor seasonal restrictions into
        # the graduation timeline risk calculation.
        course_repo = CourseRepository(self.session)
        all_course_terms = await course_repo.get_all_course_terms()

        return AuditResultResponse(
            major=audit.major,
            supported=audit.supported,
            total_ects=audit.total_ects,
            completed_ects=audit.completed_ects,
            in_progress_ects=audit.in_progress_ects,
            actual_credits_earned=audit.actual_credits_earned,
            categories=[
                CategoryResultResponse(
                    name=cat.name,
                    total_ects=cat.total_ects,
                    completed_ects=cat.completed_ects,
                    requirements=[
                        RequirementResultResponse(
                            name=req.name,
                            required_count=req.required_count,
                            completed_count=req.completed_count,
                            in_progress_count=req.in_progress_count,
                            status=req.status,
                            matched_courses=[
                                MatchedCourseResponse(code=m.code, status=m.status)
                                for m in req.matched_courses
                            ],
                            ects_per_course=req.ects_per_course,
                            note=req.note,
                            terms_available=get_terms_for_patterns(req.patterns, all_course_terms),
                        )
                        for req in cat.requirements
                    ],
                )
                for cat in audit.categories
            ],
        )

    async def get_degree_plan(self, user_id: int) -> DegreePlanResponse:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        major = (user.major or "").strip()

        stmt = (
            select(Enrollment)
            .options(course_loader())
            .where(Enrollment.user_id == user_id)
            .where(
                Enrollment.status.in_(
                    [EnrollmentStatus.PASSED, EnrollmentStatus.IN_PROGRESS]
                )
            )
        )
        result = await self.session.execute(stmt)
        enrollments = list(result.scalars().unique().all())

        courses: list[tuple[str, str]] = []
        passed_grade_pts: dict[str, float] = {}
        for e in enrollments:
            code = format_course_code(
                e.course_offering.course.code,
                e.course_offering.course.level,
            )
            courses.append((code, e.status.value))
            if e.status == EnrollmentStatus.PASSED:
                grade_str = (e.grade or "").strip().upper()
                if grade_str.startswith("P"):
                    # P/PASS (pass-fail system) — satisfies any grade requirement
                    passed_grade_pts[code] = 4.0
                else:
                    passed_grade_pts[code] = e.grade_points if e.grade_points is not None else 1.0

        enrollment_year = (
            settings.CURRENT_YEAR - user.study_year if user.study_year else None
        )

        handbook_plans = None
        if enrollment_year:
            handbook_svc = HandbookService(self.session)
            try:
                handbook_plans = await handbook_svc.get_plans_for_year(enrollment_year)
            except ProgrammingError as exc:
                if not _is_missing_handbook_table(exc):
                    raise

        audit = compute_audit(major, courses, user.total_credits_earned or 0, handbook_plans, kazakh_level=user.kazakh_level)

        if not audit.supported:
            return DegreePlanResponse(
                major=audit.major,
                graduation_term=None,
                graduation_year=None,
                needs_extra_time=False,
                enrollment_year=enrollment_year,
                terms=[],
            )

        course_repo = CourseRepository(self.session)
        all_course_terms = await course_repo.get_all_course_terms()

        current_term = settings.CURRENT_TERM
        current_year = settings.CURRENT_YEAR

        # Build per-requirement term lookups and course-term index
        terms_by_code_level: dict[tuple[str, str], list[str]] = {}
        for code, level, t in all_course_terms:
            terms_by_code_level.setdefault((code, level), []).append(t)

        # Collect slots to schedule
        in_progress_slots: list[PlannedCourseResponse] = []
        pending_slots: list[PlannedCourseResponse] = []

        # Gather elective requirement patterns → suggestions cache (by req name)
        elective_req_patterns: dict[str, list[str]] = {}
        # Core (non-elective) requirement patterns for course info lookup
        core_req_patterns: dict[str, list[str]] = {}

        for cat in audit.categories:
            for req in cat.requirements:
                terms_avail = get_terms_for_patterns(req.patterns, all_course_terms)
                base = dict(
                    requirement_name=req.name,
                    category=cat.name,
                    ects=req.ects_per_course,
                    note=req.note,
                    terms_available=terms_avail,
                    is_elective=req.is_elective,
                    depends_on=req.depends_on,
                )
                ip_codes = [m.code for m in req.matched_courses if m.status == "in_progress"]
                for code in ip_codes:
                    in_progress_slots.append(PlannedCourseResponse(**base, status="in_progress", matched_codes=[code]))
                remaining = max(0, req.required_count - req.completed_count - req.in_progress_count)
                for _ in range(remaining):
                    pending_slots.append(PlannedCourseResponse(**base, status="pending"))

                if req.is_elective and "*" not in req.patterns:
                    elective_req_patterns[req.name] = req.patterns
                elif not req.is_elective and "*" not in req.patterns:
                    core_req_patterns[req.name] = req.patterns

        # Auto-detect prerequisite ordering from DB: if course B requires course A,
        # and both are pending, B's slot must be scheduled after A's slot.
        passed_codes: set[str] = {code for code, status in courses if status == "passed"}
        # Map exact course code → requirement_name for pending non-elective slots
        code_to_req: dict[str, str] = {}
        for slot in pending_slots:
            for p in (core_req_patterns.get(slot.requirement_name) or []):
                pn = p.strip().upper()
                if " " in pn and len(pn.split(" ", 1)[1]) >= 3:
                    code_to_req[pn] = slot.requirement_name

        if code_to_req:
            # Collect extra deps: req_name → prereq_req_name (first found wins)
            auto_deps: dict[str, str] = {}
            db_courses_for_prereqs = await course_repo.get_courses_info_by_patterns(
                list(code_to_req.keys()), limit=500
            )
            for c in db_courses_for_prereqs:
                full_code = f"{c.code} {c.level}"
                req_name = code_to_req.get(full_code)
                if not req_name or not c.prerequisites or req_name in auto_deps:
                    continue
                for prereq_code, prereq_level in _COURSE_RE.findall(c.prerequisites):
                    prereq_full = f"{prereq_code} {prereq_level}"
                    if prereq_full in passed_codes:
                        # Check if a minimum grade is required (e.g. "C and above")
                        grade_match = _GRADE_REQ_RE.search(c.prerequisites)
                        if grade_match:
                            req_grade = grade_match.group(1).upper()
                            req_pts = _GRADE_POINTS_MAP.get(req_grade, 1.0)
                            student_pts = passed_grade_pts.get(prereq_full, 0.0)
                            if student_pts >= req_pts:
                                continue  # grade threshold met, no ordering needed
                            # grade insufficient — treat prereq as unmet, add constraint
                        else:
                            continue  # D is sufficient, no constraint needed
                    prereq_req = code_to_req.get(prereq_full)
                    if prereq_req and prereq_req != req_name:
                        auto_deps[req_name] = prereq_req
                        break

            if auto_deps:
                pending_slots = [
                    s.model_copy(update={"depends_on": auto_deps[s.requirement_name]})
                    if s.requirement_name in auto_deps and s.depends_on is None
                    else s
                    for s in pending_slots
                ]

        future_terms = _generate_future_terms(current_term, current_year, 25)
        future_loads: dict[tuple[str, int], list[PlannedCourseResponse]] = {
            k: [] for k in future_terms
        }

        # Track which future_terms index each requirement is scheduled at
        req_scheduled_idx: dict[str, int] = {}

        for slot in pending_slots:
            for fi, ft in enumerate(future_terms):
                t, _y = ft
                cap = _TERM_CAPACITY[t]
                if slot.terms_available and t not in slot.terms_available:
                    continue
                # Enforce prerequisite ordering: dependency must be in a strictly earlier term
                if slot.depends_on is not None:
                    dep_idx = req_scheduled_idx.get(slot.depends_on)
                    if dep_idx is None or dep_idx >= fi:
                        continue
                if len(future_loads[ft]) < cap:
                    future_loads[ft].append(slot)
                    req_scheduled_idx[slot.requirement_name] = fi
                    break

        terms_map: dict[tuple[str, int], list[PlannedCourseResponse]] = {}
        if in_progress_slots:
            terms_map[(current_term, current_year)] = list(in_progress_slots)
        for ft in future_terms:
            if future_loads[ft]:
                terms_map[ft] = future_loads[ft]

        all_keys = sorted(terms_map.keys(), key=lambda k: term_year_sort_key(k[0], k[1]))

        # Pre-fetch course suggestions for elective requirements per term type
        suggestion_cache: dict[tuple[str, str, int, int | None], list[SuggestedCourseResponse]] = {}

        async def _get_suggestions(req_name: str, term_type: str, required_ects: int, study_year: int | None) -> list[SuggestedCourseResponse]:
            key = (req_name, term_type, required_ects, study_year)
            if key in suggestion_cache:
                return suggestion_cache[key]
            patterns = elective_req_patterns.get(req_name, [])
            if not patterns:
                suggestion_cache[key] = []
                return []
            db_courses = await course_repo.get_courses_by_patterns(
                patterns, term_type, all_course_terms, limit=8, required_ects=required_ects
            )
            result_list = sorted(
                [
                    SuggestedCourseResponse(
                        code=c.code,
                        level=c.level,
                        full_code=f"{c.code} {c.level}".strip(),
                        title=c.title,
                        ects=c.ects,
                        user_priority=_get_user_priority(c, major, study_year),
                        terms_offered=sorted(set(terms_by_code_level.get((c.code, c.level), []))),
                    )
                    for c in db_courses
                ],
                key=lambda s: s.user_priority if s.user_priority is not None else 999,
            )
            suggestion_cache[key] = result_list
            return result_list

        course_info_cache: dict[tuple[str, int | None], list[SuggestedCourseResponse]] = {}

        async def _get_course_info(patterns: list[str], study_year: int | None) -> list[SuggestedCourseResponse]:
            key = (",".join(sorted(patterns)), study_year)
            if key in course_info_cache:
                return course_info_cache[key]
            # Fetch all matches (no limit), build responses, sort by priority,
            # then cap at 8 so the highest-priority courses surface first.
            db_courses = await course_repo.get_courses_info_by_patterns(patterns, limit=500)
            result_list = sorted(
                [
                    SuggestedCourseResponse(
                        code=c.code,
                        level=c.level,
                        full_code=f"{c.code} {c.level}".strip(),
                        title=c.title,
                        ects=c.ects,
                        user_priority=_get_user_priority(c, major, study_year),
                        terms_offered=sorted(set(terms_by_code_level.get((c.code, c.level), []))),
                    )
                    for c in db_courses
                ],
                key=lambda s: s.user_priority if s.user_priority is not None else 999,
            )[:8]
            course_info_cache[key] = result_list
            return result_list

        planned_terms: list[PlannedTermResponse] = []
        for tk in all_keys:
            t, y = tk
            term_study_year = _study_year_at_term(enrollment_year, t, y)
            raw_courses = terms_map[tk]
            enriched: list[PlannedCourseResponse] = []
            for slot in raw_courses:
                suggestions: list[SuggestedCourseResponse] = []
                if slot.status == "in_progress" and slot.matched_codes:
                    suggestions = await _get_course_info(slot.matched_codes, term_study_year)
                elif slot.is_elective and slot.status == "pending":
                    suggestions = await _get_suggestions(slot.requirement_name, t, slot.ects, term_study_year)
                elif not slot.is_elective and slot.status == "pending":
                    patterns = core_req_patterns.get(slot.requirement_name, [])
                    if patterns:
                        suggestions = await _get_course_info(patterns, term_study_year)
                enriched.append(slot.model_copy(update={"suggested_courses": suggestions}))

            planned_terms.append(PlannedTermResponse(
                term=t,
                year=y,
                label=_fmt_term_year(t, y),
                courses=enriched,
                total_ects=sum(c.ects for c in enriched),
                is_current=(t == current_term and y == current_year),
                study_year=_study_year_at_term(enrollment_year, t, y),
            ))

        graduation_term: str | None = None
        graduation_year: int | None = None
        if all_keys:
            graduation_term, graduation_year = all_keys[-1]

        needs_extra_time = False
        if enrollment_year and graduation_year:
            expected_year = enrollment_year + 4
            needs_extra_time = graduation_year > expected_year or (
                graduation_year == expected_year and graduation_term == "Fall"
            )

        return DegreePlanResponse(
            major=audit.major,
            graduation_term=graduation_term,
            graduation_year=graduation_year,
            needs_extra_time=needs_extra_time,
            enrollment_year=enrollment_year,
            terms=planned_terms,
        )
