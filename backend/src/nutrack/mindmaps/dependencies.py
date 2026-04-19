from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.database import get_async_session
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.mindmaps.service import MindmapService
from nutrack.storage import ObjectStorage
from nutrack.study.repository import StudyMaterialUploadRepository


def get_mindmap_service(
    session: AsyncSession = Depends(get_async_session),
) -> MindmapService:
    return MindmapService(
        repo=MindmapRepository(session),
        material_repo=StudyMaterialUploadRepository(session),
        storage=ObjectStorage(),
    )
