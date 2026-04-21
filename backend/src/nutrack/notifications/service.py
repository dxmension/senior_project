import logging
from datetime import timezone, datetime

from httpx import AsyncClient

from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.assessments.utils import assessment_label
from nutrack.assessments.repository import AssessmentRepository
from nutrack.config import settings
from nutrack.mock_exams.models import (
    MockExamGenerationJob,
    MockExamGenerationStatus,
    MockExamGenerationTrigger,
)
from nutrack.mock_exams.repository import MockExamGenerationJobRepository
from nutrack.users.repository import UserRepository

logger = logging.getLogger(__name__)
RESEND_API_URL = "https://api.resend.com/emails"


def _notifications_enabled() -> bool:
    return bool(settings.RESEND_API_KEY and settings.RESEND_FROM_EMAIL)


def _should_send(job: MockExamGenerationJob) -> bool:
    return all(
        [
            job.status == MockExamGenerationStatus.COMPLETED,
            job.trigger == MockExamGenerationTrigger.DEADLINE_REMINDER,
            job.generated_mock_exam_id is not None,
            job.notification_sent_at is None,
        ]
    )


def _deadline_label(deadline: datetime) -> str:
    local_deadline = deadline.astimezone(timezone.utc)
    return local_deadline.strftime("%Y-%m-%d %H:%M UTC")


def _message_body(
    first_name: str,
    course_label: str,
    assessment_label: str,
    deadline_label: str,
) -> str:
    return (
        f"Hi {first_name},\n\n"
        f"Your AI mock exam for {course_label} {assessment_label} is ready.\n"
        f"Your assessment is coming up soon on {deadline_label}.\n\n"
        "Open nutrack to review the mock exam and start preparing.\n"
    )


def _message_html(
    first_name: str,
    course_label: str,
    assessment_label: str,
    deadline_label: str,
) -> str:
    return f"""
<!doctype html>
<html lang="en">
  <body style="margin:0;padding:0;background:#f5f7fb;font-family:Arial,sans-serif;color:#172033;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f5f7fb;padding:32px 16px;">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="max-width:640px;background:#ffffff;border-radius:20px;overflow:hidden;">
            <tr>
              <td style="padding:28px 32px;background:linear-gradient(135deg,#0f172a,#1d4ed8);color:#ffffff;">
                <div style="font-size:12px;letter-spacing:1.6px;text-transform:uppercase;opacity:0.8;">nutrack</div>
                <h1 style="margin:12px 0 0;font-size:28px;line-height:1.2;">Your AI mock exam is ready</h1>
              </td>
            </tr>
            <tr>
              <td style="padding:32px;">
                <p style="margin:0 0 16px;font-size:16px;line-height:1.7;">Hi {first_name},</p>
                <p style="margin:0 0 16px;font-size:16px;line-height:1.7;">
                  Your AI mock exam for <strong>{course_label} {assessment_label}</strong> is ready.
                </p>
                <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:24px 0;background:#f8fafc;border:1px solid #dbe4f0;border-radius:16px;">
                  <tr>
                    <td style="padding:20px 22px;">
                      <div style="font-size:12px;text-transform:uppercase;letter-spacing:1.4px;color:#64748b;margin-bottom:8px;">Assessment deadline</div>
                      <div style="font-size:20px;font-weight:700;color:#0f172a;">{deadline_label}</div>
                      <div style="margin-top:10px;font-size:14px;line-height:1.6;color:#475569;">
                        Your assessment is tomorrow. Review the mock exam now to sharpen weak spots before the deadline.
                      </div>
                    </td>
                  </tr>
                </table>
                <p style="margin:0 0 24px;font-size:16px;line-height:1.7;">
                  Open nutrack to review the mock exam and start preparing.
                </p>
                <div style="margin:0 0 24px;">
                  <a href="https://nutrack.local/study" style="display:inline-block;background:#2563eb;color:#ffffff;text-decoration:none;font-weight:600;padding:14px 22px;border-radius:999px;">
                    Open nutrack
                  </a>
                </div>
                <p style="margin:0;font-size:13px;line-height:1.6;color:#64748b;">
                  You are receiving this because assessment notifications are enabled on your nutrack profile.
                </p>
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>
""".strip()


def _course_label(code: str, level: str | None) -> str:
    clean_level = (level or "").strip()
    if not clean_level or clean_level == "0":
        return code
    return f"{code} {clean_level}"


def _message_subject(assessment_label: str, course_label: str) -> str:
    return (
        f"Upcoming {assessment_label} on {course_label} is already tomorrow! "
        "We have prepared an AI mock for you"
    )


async def _send_message(
    to_email: str,
    subject: str,
    body: str,
    html: str,
) -> None:
    payload = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": subject,
        "text": body,
        "html": html,
    }
    headers = {
        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    async with AsyncClient(timeout=15.0) as client:
        response = await client.post(
            RESEND_API_URL,
            json=payload,
            headers=headers,
        )
    response.raise_for_status()


class NotificationsService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)
        self.job_repo = MockExamGenerationJobRepository(session)
        self.assessment_repo = AssessmentRepository(session)

    async def send_mock_exam_ready_email(
        self,
        job: MockExamGenerationJob,
    ) -> bool:
        if not _should_send(job) or not _notifications_enabled():
            return False
        user = await self.user_repo.get_by_id(job.user_id)
        if user is None or not user.subscribed_to_notifications:
            return False
        assessment = await self.assessment_repo.get_by_id_and_user(
            job.assessment_id,
            job.user_id,
        )
        if assessment is None:
            return False
        course = assessment.course_offering.course
        course_label = _course_label(course.code, course.level)
        subject = _message_subject(
            assessment_label(
                assessment.assessment_type,
                assessment.assessment_number,
            ),
            course_label,
        )
        body = _message_body(
            user.first_name,
            course_label,
            assessment_label(
                assessment.assessment_type,
                assessment.assessment_number,
            ),
            _deadline_label(assessment.deadline),
        )
        html = _message_html(
            user.first_name,
            course_label,
            assessment_label(
                assessment.assessment_type,
                assessment.assessment_number,
            ),
            _deadline_label(assessment.deadline),
        )
        await _send_message(
            user.email,
            subject,
            body,
            html,
        )
        await self.job_repo.update(
            job,
            notification_sent_at=datetime.now(timezone.utc),
        )
        logger.info("sent mock exam reminder email job_id=%s", job.id)
        return True
