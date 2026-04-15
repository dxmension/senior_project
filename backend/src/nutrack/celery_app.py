from celery import Celery

from nutrack.config import settings
from nutrack.database import load_model_modules

celery_app = Celery("NU Learning")

celery_app.config_from_object(
    {
        "broker_url": settings.CELERY_BROKER_URL,
        "result_backend": settings.CELERY_RESULT_BACKEND,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "timezone": "Asia/Almaty",
        "enable_utc": True,
        "task_track_started": True,
        "task_acks_late": True,
        "worker_prefetch_multiplier": 1,
    }
)

# Worker tasks can touch ORM models without importing the web app, so
# register all domain models before task execution configures mappers.
load_model_modules()

# Import task modules explicitly so workers register application tasks on boot.
from nutrack.tasks import materials, parse_transcript  # noqa: F401,E402
