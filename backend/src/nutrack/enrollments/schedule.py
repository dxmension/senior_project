import re
from datetime import time


_DAY_TOKENS = frozenset("MTWRFSU")
_TIME_RE = re.compile(r"(\d{1,2}):?(\d{0,2})\s*(AM|PM)?", re.IGNORECASE)


def parse_days(days_str: str | None) -> frozenset[str]:
    if not days_str:
        return frozenset()
    compact = re.sub(r"[^MTWRFSU]", "", days_str.strip().upper())
    return frozenset(c for c in compact if c in _DAY_TOKENS)


def _parse_single(s: str) -> time:
    m = _TIME_RE.match(s.strip())
    if not m:
        raise ValueError(f"Cannot parse time: {s!r}")
    h = int(m.group(1))
    mm = int(m.group(2) or 0)
    ampm = (m.group(3) or "").upper()
    if ampm == "PM" and h != 12:
        h += 12
    if ampm == "AM" and h == 12:
        h = 0
    return time(h, mm)


def parse_meeting_time(meeting_time: str | None) -> tuple[time, time] | None:
    if not meeting_time or "-" not in meeting_time:
        return None
    left, right = meeting_time.split("-", 1)
    return _parse_single(left), _parse_single(right)


def offerings_clash(
    a_days: str | None,
    a_time: str | None,
    b_days: str | None,
    b_time: str | None,
) -> bool:
    da, db = parse_days(a_days), parse_days(b_days)
    if not (da & db):
        return False
    ta = parse_meeting_time(a_time)
    tb = parse_meeting_time(b_time)
    if ta is None or tb is None:
        return False
    a_start, a_end = ta
    b_start, b_end = tb
    return a_start < b_end and b_start < a_end
