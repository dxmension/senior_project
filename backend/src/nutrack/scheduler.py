from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from nutrack.notifications.service import NotificationsService

scheduler = AsyncIOScheduler(timezone="Asia/Almaty")


scheduler.add_job(
    NotificationsService.detect_and_queue_notifications,
    trigger="interval",
    seconds=10,
    id="assessment_notification_job",
    replace_existing=True,
    misfire_grace_time=300
)
