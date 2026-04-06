from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from nutrack.courses.models import Course, CourseOffering
from nutrack.enrollments.models import Enrollment
from nutrack.users.models import User


class AdminRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[User]:
        stmt = (
            select(User)
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_by_id(self, user_id: int) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id, User.deleted_at.is_(None))
            .options(selectinload(User.enrollments))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_enrollment_count(self, user_id: int) -> int:
        stmt = select(func.count()).select_from(Enrollment).where(
            Enrollment.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def update_user(
        self,
        user: User,
        **kwargs,
    ) -> User:
        for key, value in kwargs.items():
            if value is not None:
                setattr(user, key, value)
        await self.session.flush()
        return user

    async def get_total_users_count(self) -> int:
        stmt = select(func.count()).select_from(User).where(User.deleted_at.is_(None))
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_total_courses_count(self) -> int:
        stmt = select(func.count()).select_from(Course)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_total_offerings_count(self) -> int:
        stmt = select(func.count()).select_from(CourseOffering)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_total_enrollments_count(self) -> int:
        stmt = select(func.count()).select_from(Enrollment)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_onboarded_users_count(self) -> int:
        stmt = select(func.count()).select_from(User).where(
            User.is_onboarded.is_(True),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_admin_users_count(self) -> int:
        stmt = select(func.count()).select_from(User).where(
            User.is_admin.is_(True),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_active_users_last_30_days(self) -> int:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        stmt = select(func.count()).select_from(User).where(
            User.updated_at >= cutoff_date,
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_average_cgpa(self) -> float | None:
        stmt = select(func.avg(User.cgpa)).where(
            User.cgpa.isnot(None),
            User.deleted_at.is_(None),
        )
        result = await self.session.execute(stmt)
        avg = result.scalar_one_or_none()
        return float(avg) if avg else None

    async def get_users_by_study_year(self) -> dict[int, int]:
        stmt = (
            select(User.study_year, func.count())
            .where(User.study_year.isnot(None), User.deleted_at.is_(None))
            .group_by(User.study_year)
        )
        result = await self.session.execute(stmt)
        return {year: count for year, count in result.all()}

    async def get_users_by_major(self) -> dict[str, int]:
        stmt = (
            select(User.major, func.count())
            .where(User.major.isnot(None), User.deleted_at.is_(None))
            .group_by(User.major)
        )
        result = await self.session.execute(stmt)
        return {major: count for major, count in result.all()}

    async def get_database_size_mb(self) -> float | None:
        try:
            stmt = text("SELECT pg_database_size(current_database()) / 1048576.0")
            result = await self.session.execute(stmt)
            size = result.scalar_one_or_none()
            return float(size) if size else None
        except Exception:
            return None

    async def get_table_count(self) -> int:
        try:
            stmt = text(
                """
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                """
            )
            result = await self.session.execute(stmt)
            return result.scalar_one()
        except Exception:
            return 0

    async def search_users(
        self,
        query: str,
        limit: int = 20,
    ) -> list[User]:
        search_pattern = f"%{query.lower()}%"
        stmt = (
            select(User)
            .where(
                User.deleted_at.is_(None),
                (func.lower(User.email).like(search_pattern))
                | (func.lower(User.first_name).like(search_pattern))
                | (func.lower(User.last_name).like(search_pattern)),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def soft_delete_user(self, user: User) -> None:
        stmt = (
            update(User)
            .where(User.id == user.id)
            .values(deleted_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)
        await self.session.flush()

    async def get_all_courses(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Course]:
        stmt = (
            select(Course)
            .order_by(Course.code, Course.level)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_course_by_id(self, course_id: int) -> Course | None:
        return await self.session.get(Course, course_id)

    async def update_course(
        self,
        course: Course,
        **kwargs,
    ) -> Course:
        for key, value in kwargs.items():
            if value is not None:
                setattr(course, key, value)
        await self.session.flush()
        return course

    async def search_courses(
        self,
        query: str,
        limit: int = 50,
    ) -> list[Course]:
        search_pattern = f"%{query.lower()}%"
        stmt = (
            select(Course)
            .where(
                (func.lower(Course.code).like(search_pattern))
                | (func.lower(Course.title).like(search_pattern))
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
