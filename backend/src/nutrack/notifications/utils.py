"""Utility functions for the notifications module."""

from datetime import datetime, timezone

from nutrack.assessments.repository import AssessmentRepository

_DEADLINE_FMT = "%A, %B %d at %I:%M %p UTC"
_DEDUP_KEY = "notif:sent:{user_id}:{assessment_id}"


def _humanise_deadline(iso_deadline: str) -> str:
    dt = datetime.fromisoformat(iso_deadline)
    dt_utc = dt.astimezone(timezone.utc)
    return dt_utc.strftime(_DEADLINE_FMT)


def _hours_until(iso_deadline: str) -> float:
    dt = datetime.fromisoformat(iso_deadline).astimezone(timezone.utc)
    delta = dt - datetime.now(tz=timezone.utc)
    return delta.total_seconds() / 3600


def _build_email(
    first_name: str,
    assessments: list[dict],
) -> tuple[str, str]:
    count = len(assessments)
    noun = "assessment" if count == 1 else "assessments"
    verb = "is" if count == 1 else "are"

    subject = f"Nutrack: {count} upcoming {noun} due soon"

    lines: list[str] = [
        f"Hi {first_name},",
        "",
        f"You have {count} upcoming {noun} that {verb} due within the next 3 days:",
        "",
    ]

    for a in sorted(assessments, key=lambda x: x["deadline"]):
        hours = _hours_until(a["deadline"])
        urgency = f"in ~{hours:.0f} h" if hours < 48 else _humanise_deadline(a["deadline"])  # noqa: E501
        lines.append(
            f"  • [{a['assessment_type'].upper()}] {a['title']}\n"
            f"    Course : {a['course_code']} — {a['course_title']}\n"
            f"    Due    : {_humanise_deadline(a['deadline'])}  ({urgency})"
        )

    lines += [
        "",
        "Good luck with your studies!",
        "",
        "— The Nutrack Team",
        "",
        "─────────────────────────────────────────",
        "You are receiving this because you opted into assessment reminders.",
        "You can manage your notification preferences from your Nutrack profile.",
    ]

    return subject, "\n".join(lines)


def _build_course_code(assessment) -> str:
    course = assessment.course_offering.course
    level = (course.level or "").strip()
    return f"{course.code} {level}" if level and level != "0" else course.code


async def _process_user(user, assessment_repo: AssessmentRepository, redis, now: datetime) -> None:  # type: ignore[no-untyped-def]
    assessments = await assessment_repo.get_upcoming_by_window(
        user.id,
        hours_until=72,  # LOOKAHEAD_HOURS
        # assessment_types=None → returns every type (homework, quiz, lab, …)
        # include_completed=False (default) → silently skips already-done work
    )

    if not assessments:
        return  # Let caller handle logging

    new_assessments = []
    for assessment in assessments:
        dedup_key = _DEDUP_KEY.format(user_id=user.id, assessment_id=assessment.id)
        already_notified = await redis.exists(dedup_key)
        if not already_notified:
            new_assessments.append(assessment)

    if not new_assessments:
        return  # Let caller handle logging

    payload: list[dict] = [
        {
            "id": a.id,
            "title": a.title,
            "assessment_type": a.assessment_type.value,
            "course_id": a.course_id,  # course_offerings.id — used to build the deep-link URL
            "course_code": _build_course_code(a),
            "course_title": a.course_offering.course.title,
            "deadline": a.deadline.isoformat(),
        }
        for a in new_assessments
    ]

    from nutrack.notifications.tasks import send_assessment_notification_task
    
    send_assessment_notification_task.apply_async(
        kwargs={
            "user_email": user.email,
            "user_first_name": user.first_name or "Student",
            "assessments": payload,
        }
    )

    for assessment in new_assessments:
        dedup_key = _DEDUP_KEY.format(user_id=user.id, assessment_id=assessment.id)
        ttl_seconds = max(int((assessment.deadline - now).total_seconds()), 1)
        await redis.set(dedup_key, "1", ex=ttl_seconds)

    # Return stats for logging
    return {
        "new_assessments": len(new_assessments),
        "total_assessments": len(assessments),
    }