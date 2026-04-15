import asyncio

from nutrack.celery_app import celery_app
from nutrack.database import AsyncSessionLocal
from nutrack.study.service import StudyService


async def _run_upload(upload_id: int) -> None:
    async with AsyncSessionLocal() as session:
        service = StudyService(session=session)
        try:
            await service.process_upload(upload_id)
        except Exception:
            await session.rollback()
            raise


async def _mark_failed(upload_id: int, message: str) -> None:
    async with AsyncSessionLocal() as session:
        service = StudyService(session=session)
        await service.mark_upload_failed(upload_id, message)


@celery_app.task(
    bind=True,
    name="nutrack.tasks.materials.upload_course_material_task",
    max_retries=2,
    default_retry_delay=10,
)
def upload_course_material_task(self, upload_id: int) -> None:
    try:
        asyncio.run(_run_upload(upload_id))
    except Exception as exc:
        if self.request.retries >= self.max_retries:
            asyncio.run(_mark_failed(upload_id, str(exc)))
            raise
        raise self.retry(exc=exc)
