import asyncio
import logging

from nutrack.celery_app import celery_app
from nutrack.database import AsyncSessionLocal
from nutrack.mock_exams.generation import MockExamGenerationService
from nutrack.notifications.service import NotificationsService

logger = logging.getLogger(__name__)


async def _run_generation(job_id: int, task_id: str | None) -> None:
    async with AsyncSessionLocal() as session:
        service = MockExamGenerationService(session=session)
        notifications = NotificationsService(session=session)
        if task_id is not None:
            await service.set_celery_task_id(job_id, task_id)
        try:
            job = await service.run_job(job_id)
            await session.commit()
            await _send_ready_notification(notifications, job, session)
        except Exception:
            await session.rollback()
            raise
        logger.info(
            "mock exam generation finished job_id=%s task_id=%s status=%s "
            "reason=%s generated_mock_exam_id=%s",
            job_id,
            task_id,
            job.status.value,
            job.error_message,
            job.generated_mock_exam_id,
        )


async def _send_ready_notification(
    notifications: NotificationsService,
    job,
    session,
) -> None:
    try:
        sent = await notifications.send_mock_exam_ready_email(job)
        if sent:
            await session.commit()
    except Exception:
        await session.rollback()
        logger.exception(
            "failed to send mock exam reminder email job_id=%s",
            job.id,
        )


async def _reset_job(job_id: int, message: str, task_id: str | None) -> None:
    async with AsyncSessionLocal() as session:
        service = MockExamGenerationService(session=session)
        await service.reset_job_to_queued(job_id, message, task_id)
        await session.commit()


@celery_app.task(
    bind=True,
    name="nutrack.mock_exams.tasks.generate_assessment_mock_exam_task",
    max_retries=2,
    default_retry_delay=30,
)
def generate_assessment_mock_exam_task(self, job_id: int) -> None:
    task_id = getattr(self.request, "id", None)
    try:
        asyncio.run(_run_generation(job_id, task_id))
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            raise
        asyncio.run(_reset_job(job_id, str(exc), task_id))
        raise self.retry(exc=exc)
