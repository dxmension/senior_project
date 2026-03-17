from fastapi import APIRouter

from nutrack.auth.router import router as auth_router
from nutrack.courses.router import router as courses_router
from nutrack.enrollments.router import router as enrollments_router
from nutrack.flashcards.router import router as flashcards_router
from nutrack.notifications.router import router as notifications_router
from nutrack.study.router import router as study_router
from nutrack.transcripts.router import router as transcripts_router
from nutrack.users.router import router as users_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(transcripts_router)
api_router.include_router(courses_router)
api_router.include_router(enrollments_router)
api_router.include_router(study_router)
api_router.include_router(flashcards_router)
api_router.include_router(notifications_router)
