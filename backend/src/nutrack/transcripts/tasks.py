import logging

from nutrack.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(
    name="nutrack.transcripts.tasks.parse_transcript_task",
    bind=True,
    max_retries=2,
    default_retry_delay=10,
)
def parse_transcript_task(self, transcript_id: str) -> None:
    logger.warning("parse_transcript_task is currently a placeholder: %s", transcript_id)
