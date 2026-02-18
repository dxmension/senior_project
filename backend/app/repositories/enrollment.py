from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollment import Enrollment
from app.repositories.base import BaseRepository


class EnrollmentRepository(BaseRepository[Enrollment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Enrollment)

    async def get_by_user_id(self, user_id: int) -> list[Enrollment]:
        stmt = select(Enrollment).where(Enrollment.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_course(
        self, user_id: int, course_id: int, semester: str
    ) -> Enrollment | None:
        stmt = select(Enrollment).where(
            Enrollment.user_id == user_id,
            Enrollment.course_id == course_id,
            Enrollment.semester == semester,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
