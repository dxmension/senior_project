from fastapi import APIRouter



from nutrack.admin.router import router as admin_router

from nutrack.assessments.router import router as assessments_router

from nutrack.auth.router import router as auth_router

from nutrack.handbook.router import router as handbook_router

from nutrack.insights.router import router as insights_router

from nutrack.calendar.router import router as calendar_router

from nutrack.config import settings

from nutrack.course_materials.router import router as course_materials_router

from nutrack.courses.router import router as courses_router

from nutrack.dashboard.router import router as dashboard_router

from nutrack.enrollments.router import router as enrollments_router

from nutrack.events.router import router as events_router

from nutrack.flashcards.router import router as flashcards_router

from nutrack.mindmaps.router import router as mindmaps_router

from nutrack.mock_exams.router import router as mock_exams_router

from nutrack.notifications.router import router as notifications_router

from nutrack.study_helper.router import router as study_helper_router

from nutrack.transcripts.router import router as transcripts_router

from nutrack.users.router import router as users_router



api_router = APIRouter(prefix=settings.API_V1_PREFIX)



api_router.include_router(auth_router)


api_router.include_router(users_router)

api_router.include_router(transcripts_router)

api_router.include_router(courses_router)

api_router.include_router(enrollments_router)

api_router.include_router(assessments_router, prefix="/assessments")

api_router.include_router(events_router, prefix="/events")

api_router.include_router(calendar_router, prefix="/calendar")

api_router.include_router(dashboard_router, prefix="/dashboard")

api_router.include_router(insights_router, prefix="/insights")

api_router.include_router(mindmaps_router)

api_router.include_router(course_materials_router)

api_router.include_router(mock_exams_router)

api_router.include_router(flashcards_router)

api_router.include_router(notifications_router)

api_router.include_router(admin_router)

api_router.include_router(handbook_router)

api_router.include_router(study_helper_router)
