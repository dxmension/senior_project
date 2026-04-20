from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.course_materials.service import CourseMaterialService
from nutrack.database import get_async_session


def get_course_material_service(
    session: AsyncSession = Depends(get_async_session),
) -> CourseMaterialService:
    return CourseMaterialService(session=session)
