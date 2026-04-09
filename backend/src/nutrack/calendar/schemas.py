import enum
from datetime import datetime
from typing import Any

from pydantic import BaseModel


class CalendarEventType(str, enum.Enum):
    PERSONAL_EVENT = "personal_event"
    ASSESSMENT_DEADLINE = "assessment_deadline"
    COURSE_SESSION = "course_session"


class CalendarEntry(BaseModel):
    id: int
    event_type: CalendarEventType
    title: str
    description: str | None
    start_at: datetime
    end_at: datetime | None
    is_all_day: bool
    location: str | None
    color: str | None
    category_name: str | None
    source_meta: dict[str, Any]
