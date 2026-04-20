from nutrack.course_materials.repository import CourseMaterialUploadRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.mindmaps.service import MindmapService
from nutrack.storage import ObjectStorage


def get_mindmap_service(
    session: AsyncSession = Depends(get_async_session),
) -> MindmapService:
    return MindmapService(
        repo=MindmapRepository(session),
        material_repo=CourseMaterialUploadRepository(session),
        storage=ObjectStorage(),
    )
