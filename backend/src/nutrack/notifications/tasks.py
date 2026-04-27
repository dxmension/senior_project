from __future__ import annotations

import logging

from nutrack.celery_app import celery_app
from nutrack.notifications.service import NotificationsService
from nutrack.notifications.templates import build_html_email
from nutrack.notifications.utils import _build_email

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    name="nutrack.notifications.tasks.send_assessment_notification_task",
    max_retries=3,
    default_retry_delay=90,
)
def send_assessment_notification_task(
    self,
    user_email: str,
    user_first_name: str,
    assessments: list[dict],
) -> None:
    if not assessments:
        logger.warning(
            "send_assessment_notification_task called with empty payload for %s — "
            "skipping silently.",
            user_email,
        )
        return

    first_name = user_first_name or "Student"
    subject, body = _build_email(first_name, assessments)
    html = build_html_email(first_name, assessments)

    try:
        NotificationsService.send_email(
            email=user_email,
            subject=subject,
            text=body,
            html=html,
        )
        logger.info(
            "Assessment notification delivered to %s (%d item(s)).",
            user_email,
            len(assessments),
        )

    except Exception as exc:
        logger.exception(
            "Failed to send notification to %s (attempt %d/%d): %s",
            user_email,
            self.request.retries + 1,
            self.max_retries + 1,
            exc,
        )
        raise self.retry(exc=exc)
