from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.course_materials.repository import CourseMaterialUploadRepository
from nutrack.database import get_async_session
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.storage import ObjectStorage
from nutrack.study_helper.repository import (
    StudyGuideRepository,
    WeekOverviewCacheRepository,
)
from nutrack.study_helper.service import StudyHelperService


def get_study_helper_service(
    session: AsyncSession = Depends(get_async_session),
) -> StudyHelperService:
    return StudyHelperService(
        repo=StudyGuideRepository(session),
        week_cache_repo=WeekOverviewCacheRepository(session),
        mindmap_repo=MindmapRepository(session),
        material_repo=CourseMaterialUploadRepository(session),
        storage=ObjectStorage(),
    )
