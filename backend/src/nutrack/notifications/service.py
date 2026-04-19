import resend
import logging
from datetime import datetime, timezone

from nutrack.assessments.repository import AssessmentRepository
from nutrack.config import settings
from nutrack.database import AsyncSessionLocal
from nutrack.notifications.utils import _process_user
from nutrack.redis import get_redis
from nutrack.users.repository import UserRepository

logger = logging.getLogger(__name__)


class NotificationsService:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def send_email(
        email: str,
        subject: str,
        text: str,
        html: str | None = None,
    ) -> None:
        try:
            resend.api_key = settings.RESEND_API_KEY
            payload: dict = {
                "from": "notifications@nutrack.online",
                "to": email,
                "subject": subject,
                "text": text,
            }
            if html:
                payload["html"] = html
            resend.Emails.send(payload)
            logger.info("Email sent successfully to %s", email)
        except Exception as exc:
            logger.exception("Failed to send email to %s: %s", email, exc)
            raise
    
    @staticmethod
    async def detect_and_queue_notifications() -> None:
        logger.info("Assessment notification job started.")
        now = datetime.now(tz=timezone.utc)
        
        redis = await get_redis()
        
        async with AsyncSessionLocal() as session:
            user_repo = UserRepository(session)
            assessment_repo = AssessmentRepository(session)
            
            subscribed_users = await user_repo.get_subscribed_users()
            logger.info(
                "Notification job: processing %d subscribed user(s).",
                len(subscribed_users),
            )
            
            for user in subscribed_users:
                try:
                    result = await _process_user(
                        user=user,
                        assessment_repo=assessment_repo,
                        redis=redis,
                        now=now,
                    )
                    if result:
                        logger.info(
                            "Notification job: queued email for user %d (%d new assessment(s), "
                            "%d already notified).",
                            user.id,
                            result["new_assessments"],
                            result["total_assessments"] - result["new_assessments"],
                        )
                    else:
                        logger.debug(
                            "Notification job: user %d has no upcoming assessments or all already notified.",
                            user.id,
                        )
                except Exception:
                    logger.exception(
                        "Notification job: unhandled error for user %d — skipping.",
                        user.id,
                    )
        
        logger.info("Assessment notification job finished.")