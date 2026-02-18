from celery import Celery

from app.config import settings

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
        "worker_prefetch_multiplier": 1
    }
)

celery_app.autodiscover_tasks(["app.tasks"])
