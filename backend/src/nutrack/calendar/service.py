import re
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import and_, select
from sqlalchemy.orm import joinedload

from nutrack.assessments.models import Assessment
from nutrack.assessments.repository import AssessmentRepository
from nutrack.assessments.utils import assessment_label
from nutrack.calendar.schemas import CalendarEntry, CalendarEventType
from nutrack.courses.models import CourseOffering
from nutrack.enrollments.models import Enrollment, EnrollmentStatus
from nutrack.enrollments.repository import EnrollmentRepository
from nutrack.events.service import EventService

# ---------------------------------------------------------------------------
# Day-string parsing
# ---------------------------------------------------------------------------

_WEEKDAY_WORDS: list[tuple[str, int]] = [
    ("monday", 0),
    ("tuesday", 1),
    ("wednesday", 2),
    ("thursday", 3),
    ("friday", 4),
    ("saturday", 5),
    ("sunday", 6),
    ("mon", 0),
    ("tue", 1),
    ("wed", 2),
    ("thu", 3),
    ("fri", 4),
    ("sat", 5),
    ("sun", 6),
]


def _parse_compact_days(s: str) -> set[int]:
    result: set[int] = set()
    i = 0
    s = s.lower()
    while i < len(s):
        chunk2 = s[i : i + 2]
        if chunk2 == "th":
            result.add(3)
            i += 2
        elif chunk2 == "su":
            result.add(6)
            i += 2
        elif s[i] == "m":
            result.add(0)
            i += 1
        elif s[i] == "t":
            result.add(1)
            i += 1
        elif s[i] == "w":
            result.add(2)
            i += 1
        elif s[i] == "f":
            result.add(4)
            i += 1
        elif s[i] == "s":
            result.add(5)
            i += 1
        else:
            i += 1
    return result


def _parse_days(days_str: str | None) -> list[int]:
    if not days_str:
        return []
    normalized = days_str.replace(",", " ").replace("/", " ").strip().lower()
    result: set[int] = set()
    for word in normalized.split():
        matched = False
        for name, day in _WEEKDAY_WORDS:
            if word == name:
                result.add(day)
                matched = True
                break
        if not matched:
            result.update(_parse_compact_days(word))
    if not result:
        result.update(_parse_compact_days(normalized))
    return sorted(result)


# ---------------------------------------------------------------------------
# Meeting-time parsing
# ---------------------------------------------------------------------------

_TIME_PATTERN = re.compile(r"(\d{1,2}):(\d{2})\s*(AM|PM|am|pm)?")


def _to_time(hour: str, minute: str, ampm: str) -> time:
    h, m = int(hour), int(minute)
    if ampm:
        if ampm.lower() == "pm" and h != 12:
            h += 12
        elif ampm.lower() == "am" and h == 12:
            h = 0
    return time(h, m)


def _parse_meeting_time(
    meeting_time_str: str | None,
) -> tuple[time | None, time | None]:
    if not meeting_time_str:
        return None, None
    matches = _TIME_PATTERN.findall(meeting_time_str)
    if len(matches) >= 2:
        return _to_time(*matches[0]), _to_time(*matches[1])
    if len(matches) == 1:
        return _to_time(*matches[0]), None
    return None, None


# ---------------------------------------------------------------------------
# Calendar entry builders
# ---------------------------------------------------------------------------


def _entry_from_personal_event(event_response) -> CalendarEntry:
    return CalendarEntry(
        id=event_response.id,
        event_type=CalendarEventType.PERSONAL_EVENT,
        title=event_response.title,
        description=event_response.description,
        start_at=event_response.start_at,
        end_at=event_response.end_at,
        is_all_day=event_response.is_all_day,
        location=event_response.location,
        color=event_response.category.color if event_response.category else None,
        category_name=event_response.category.name if event_response.category else None,
        source_meta={
            "event_id": event_response.id,
            "recurrence": event_response.recurrence.value,
        },
    )


def _entry_from_assessment(assessment: Assessment) -> CalendarEntry:
    course = assessment.course_offering.course
    return CalendarEntry(
        id=assessment.id,
        event_type=CalendarEventType.ASSESSMENT_DEADLINE,
        title=assessment_label(
            assessment.assessment_type,
            assessment.assessment_number,
        ),
        description=None,
        start_at=assessment.deadline,
        end_at=assessment.deadline,
        is_all_day=False,
        location=None,
        color=None,
        category_name=None,
        source_meta={
            "assessment_id": assessment.id,
            "assessment_type": assessment.assessment_type.value,
            "course_id": assessment.course_id,
            "course_code": f"{course.code} {course.level}".strip() if course else "",
            "is_completed": assessment.is_completed,
        },
    )


def _entry_from_course_session(
    offering: CourseOffering,
    session_date: date,
    start_time: time | None,
    end_time: time | None,
) -> CalendarEntry:
    tz = timezone.utc
    if start_time:
        start_at = datetime.combine(session_date, start_time, tzinfo=tz)
        end_at = datetime.combine(session_date, end_time, tzinfo=tz) if end_time else None
    else:
        start_at = datetime.combine(session_date, time(0, 0), tzinfo=tz)
        end_at = None

    course = offering.course
    course_code = f"{course.code} {course.level}".strip() if course.level else course.code
    return CalendarEntry(
        id=offering.id,
        event_type=CalendarEventType.COURSE_SESSION,
        title=f"{course_code}: {course.title}",
        description=None,
        start_at=start_at,
        end_at=end_at,
        is_all_day=start_time is None,
        location=offering.room,
        color=None,
        category_name=None,
        source_meta={
            "course_id": offering.course_id,
            "course_code": course_code,
            "course_title": course.title,
            "room": offering.room,
            "faculty": offering.faculty,
        },
    )


# ---------------------------------------------------------------------------
# CalendarService
# ---------------------------------------------------------------------------


class CalendarService:
    def __init__(
        self,
        event_service: EventService,
        assessment_repo: AssessmentRepository,
        enrollment_repo: EnrollmentRepository,
    ) -> None:
        self.event_service = event_service
        self.assessment_repo = assessment_repo
        self.enrollment_repo = enrollment_repo

    async def get_calendar(
        self,
        user_id: int,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[CalendarEntry]:
        entries: list[CalendarEntry] = []

        # 1. Personal events (with recurrence expansion)
        personal_events = await self.event_service.list_events(user_id, from_dt, to_dt)
        entries.extend(_entry_from_personal_event(e) for e in personal_events)

        # 2. Assessment deadlines
        assessments = await self._fetch_assessments(user_id, from_dt, to_dt)
        entries.extend(_entry_from_assessment(a) for a in assessments)

        # 3. Course sessions from active enrollments
        offerings = await self._fetch_active_offerings(user_id)
        for offering in offerings:
            sessions = _expand_course_sessions(offering, from_dt, to_dt)
            entries.extend(sessions)

        entries.sort(key=lambda e: e.start_at)
        return entries

    async def _fetch_active_offerings(
        self, user_id: int
    ) -> list[CourseOffering]:
        stmt = (
            select(CourseOffering)
            .join(Enrollment, Enrollment.course_id == CourseOffering.id)
            .options(joinedload(CourseOffering.course))
            .where(
                Enrollment.user_id == user_id,
                Enrollment.status == EnrollmentStatus.IN_PROGRESS,
            )
        )
        result = await self.enrollment_repo.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def _fetch_assessments(
        self, user_id: int, from_dt: datetime, to_dt: datetime
    ) -> list[Assessment]:
        from nutrack.assessments.models import Assessment as AssessmentModel

        stmt = (
            select(AssessmentModel)
            .options(joinedload(AssessmentModel.course_offering).joinedload(CourseOffering.course))
            .where(
                and_(
                    AssessmentModel.user_id == user_id,
                    AssessmentModel.deadline >= from_dt,
                    AssessmentModel.deadline <= to_dt,
                )
            )
            .order_by(AssessmentModel.deadline.asc())
        )
        result = await self.assessment_repo.session.execute(stmt)
        return list(result.scalars().unique().all())


# ---------------------------------------------------------------------------
# Course session expansion (pure Python)
# ---------------------------------------------------------------------------


def _expand_course_sessions(
    offering: CourseOffering,
    from_dt: datetime,
    to_dt: datetime,
) -> list[CalendarEntry]:
    weekdays = _parse_days(offering.days)
    if not weekdays:
        return []

    start_time, end_time = _parse_meeting_time(offering.meeting_time)

    range_start = from_dt.date()
    range_end = to_dt.date()
    course_start = offering.start_date or range_start
    course_end = offering.end_date or range_end

    effective_start = max(range_start, course_start)
    effective_end = min(range_end, course_end)

    if effective_start > effective_end:
        return []

    sessions: list[CalendarEntry] = []
    current = effective_start
    while current <= effective_end:
        if current.weekday() in weekdays:
            sessions.append(
                _entry_from_course_session(offering, current, start_time, end_time)
            )
        current += timedelta(days=1)

    return sessions
