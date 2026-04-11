from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.assessments.models import Assessment
from nutrack.courses.models import CourseOffering
from nutrack.database import BaseRepository


def _offering_loader():
    return joinedload(Assessment.course_offering).joinedload(CourseOffering.course)


class AssessmentRepository(BaseRepository[Assessment]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Assessment)

    async def get_by_user(
        self,
        user_id: int,
        *,
        course_id: int | None = None,
        upcoming_only: bool = False,
        completed: bool | None = None,
    ) -> list[Assessment]:
        stmt = (
            select(Assessment)
            .options(_offering_loader())
            .where(Assessment.user_id == user_id)
        )
        if course_id is not None:
            stmt = stmt.where(Assessment.course_id == course_id)
        if upcoming_only:
            now = datetime.now(tz=timezone.utc)
            stmt = stmt.where(Assessment.deadline >= now)
        if completed is not None:
            stmt = stmt.where(Assessment.is_completed == completed)
        stmt = stmt.order_by(Assessment.deadline.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_id_and_user(
        self,
        assessment_id: int,
        user_id: int,
    ) -> Assessment | None:
        stmt = (
            select(Assessment)
            .options(_offering_loader())
            .where(
                Assessment.id == assessment_id,
                Assessment.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id_and_user(
        self,
        assessment_id: int,
        user_id: int,
    ) -> bool:
        assessment = await self.get_by_id_and_user(assessment_id, user_id)
        if not assessment:
            return False
        await self.session.delete(assessment)
        await self.session.flush()
        return True
