from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.assessments.models import Assessment, AssessmentType
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
        
    async def get_major_assessments(
        self,
        user_id: int,
        days_until: int = 1,
    ) -> list[Assessment]:
        now = datetime.now(tz=timezone.utc)
        target_date = now + timedelta(days=days_until)  # fix: was timezone.timedelta

        stmt = (
            select(Assessment)
            .options(_offering_loader())
            .where(
                Assessment.user_id == user_id,
                Assessment.assessment_type.in_([
                    AssessmentType.QUIZ,
                    AssessmentType.MIDTERM,
                    AssessmentType.FINAL,
                ]),
                Assessment.deadline >= now,
                Assessment.deadline <= target_date,
            )
            .order_by(Assessment.deadline.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_upcoming_by_window(
        self,
        user_id: int,
        *,
        hours_until: int,
        assessment_types: list[AssessmentType] | None = None,
        include_completed: bool = False,
    ) -> list[Assessment]:
        now = datetime.now(tz=timezone.utc)
        window_end = now + timedelta(hours=hours_until)

        stmt = (
            select(Assessment)
            .options(_offering_loader())
            .where(
                Assessment.user_id == user_id,
                Assessment.deadline >= now,
                Assessment.deadline <= window_end,
            )
            .order_by(Assessment.deadline.asc())
        )

        if assessment_types is not None:
            stmt = stmt.where(Assessment.assessment_type.in_(assessment_types))

        if not include_completed:
            stmt = stmt.where(Assessment.is_completed.is_(False))

        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())
        