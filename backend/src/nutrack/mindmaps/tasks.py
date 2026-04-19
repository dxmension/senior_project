import asyncio

from nutrack.celery_app import celery_app
from nutrack.course_materials.repository import CourseMaterialUploadRepository
from nutrack.database import AsyncSessionLocal
from nutrack.logging import get_logger, log_step
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.mindmaps.schemas import GenerateMindmapRequest
from nutrack.mindmaps.service import MindmapService

logger = get_logger(__name__)


async def _run_generation(user_id: int, course_id: int, payload: dict) -> dict[str, int]:
    async with AsyncSessionLocal() as session:
        try:
            request = GenerateMindmapRequest.model_validate(payload)
            service = MindmapService(
                repo=MindmapRepository(session),
                material_repo=CourseMaterialUploadRepository(session),
            )
            mindmap = await service.generate_and_save(user_id, course_id, request)
            await session.commit()
            return {"mindmap_id": mindmap.id}
        except Exception:
            await session.rollback()
            raise


@celery_app.task(
    bind=True,
    name="nutrack.mindmaps.tasks.generate_mindmap_task",
    max_retries=2,
    default_retry_delay=10,
)
def generate_mindmap_task(
    self,
    user_id: int,
    course_id: int,
    payload: dict,
) -> dict[str, int]:
    log_step(
        logger,
        "mindmap_task_started",
        task_id=self.request.id,
        user_id=user_id,
        course_id=course_id,
        week=payload.get("week"),
        depth=payload.get("depth"),
    )
    try:
        result = asyncio.run(_run_generation(user_id, course_id, payload))
        log_step(
            logger,
            "mindmap_task_completed",
            task_id=self.request.id,
            user_id=user_id,
            course_id=course_id,
            mindmap_id=result["mindmap_id"],
        )
        return result
    except Exception as exc:
        log_step(
            logger,
            "mindmap_task_failed",
            task_id=self.request.id,
            retries=self.request.retries,
            error=str(exc),
        )
        raise
