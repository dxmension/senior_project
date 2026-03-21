from redis.asyncio import Redis
from sqlalchemy import exc

from nutrack.admin.exceptions import CannotModifySelfError, UserNotFoundError
from nutrack.admin.repository import AdminRepository
from nutrack.admin.schemas import (
    AnalyticsOverview,
    CourseListItem,
    DatabaseHealth,
    DatabaseStats,
    UserDetail,
    UserListItem,
)


class AdminService:
    def __init__(
        self,
        repository: AdminRepository,
        redis: Redis,
    ):
        self.repository = repository
        self.redis = redis

    async def get_all_users(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserListItem]:
        users = await self.repository.get_all_users(skip, limit)
        return [UserListItem.model_validate(user) for user in users]

    async def get_user_detail(self, user_id: int) -> UserDetail:
        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        enrollment_count = len(user.enrollments) if user.enrollments else 0

        return UserDetail(
            id=user.id,
            email=user.email,
            google_id=user.google_id,
            first_name=user.first_name,
            last_name=user.last_name,
            major=user.major,
            study_year=user.study_year,
            cgpa=user.cgpa,
            total_credits_earned=user.total_credits_earned,
            total_credits_enrolled=user.total_credits_enrolled,
            avatar_url=user.avatar_url,
            is_onboarded=user.is_onboarded,
            is_admin=user.is_admin,
            created_at=user.created_at,
            updated_at=user.updated_at,
            enrollment_count=enrollment_count,
        )

    async def update_user(
        self,
        user_id: int,
        current_user_id: int,
        is_admin: bool | None = None,
        is_onboarded: bool | None = None,
        major: str | None = None,
        study_year: int | None = None,
    ) -> UserDetail:
        if user_id == current_user_id and is_admin is not None:
            raise CannotModifySelfError()

        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        update_data = {}
        if is_admin is not None:
            update_data["is_admin"] = is_admin
        if is_onboarded is not None:
            update_data["is_onboarded"] = is_onboarded
        if major is not None:
            update_data["major"] = major
        if study_year is not None:
            update_data["study_year"] = study_year

        updated_user = await self.repository.update_user(user, **update_data)
        return await self.get_user_detail(updated_user.id)

    async def search_users(self, query: str, limit: int = 20) -> list[UserListItem]:
        users = await self.repository.search_users(query, limit)
        return [UserListItem.model_validate(user) for user in users]

    async def delete_user(
        self,
        user_id: int,
        current_user_id: int,
    ) -> None:
        if user_id == current_user_id:
            raise CannotModifySelfError()

        user = await self.repository.get_user_by_id(user_id)
        if not user:
            raise UserNotFoundError(user_id)

        await self.repository.delete_user(user)

    async def get_database_stats(self) -> DatabaseStats:
        total_users = await self.repository.get_total_users_count()
        total_courses = await self.repository.get_total_courses_count()
        total_enrollments = await self.repository.get_total_enrollments_count()

        return DatabaseStats(
            total_users=total_users,
            total_courses=total_courses,
            total_enrollments=total_enrollments,
        )

    async def get_analytics(self) -> AnalyticsOverview:
        total_users = await self.repository.get_total_users_count()
        active_users = await self.repository.get_active_users_last_30_days()
        total_courses = await self.repository.get_total_courses_count()
        total_offerings = await self.repository.get_total_offerings_count()
        total_enrollments = await self.repository.get_total_enrollments_count()
        users_by_year = await self.repository.get_users_by_study_year()
        users_by_major = await self.repository.get_users_by_major()

        return AnalyticsOverview(
            total_users=total_users,
            active_users_last_30_days=active_users,
            total_courses=total_courses,
            total_course_offerings=total_offerings,
            total_enrollments=total_enrollments,
            users_by_study_year=users_by_year,
            users_by_major=users_by_major,
        )

    async def get_database_health(self) -> DatabaseHealth:
        db_connected = await self._check_db_connection()
        redis_connected = await self._check_redis_connection()
        db_size = await self.repository.get_database_size_mb()

        return DatabaseHealth(
            database_connected=db_connected,
            redis_connected=redis_connected,
            database_size_mb=db_size,
        )

    async def get_all_courses(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> list[CourseListItem]:
        courses = await self.repository.get_all_courses(skip, limit)
        return [CourseListItem.model_validate(course) for course in courses]

    async def search_courses(
        self,
        query: str,
        limit: int = 50,
    ) -> list[CourseListItem]:
        courses = await self.repository.search_courses(query, limit)
        return [CourseListItem.model_validate(course) for course in courses]

    async def update_course(
        self,
        course_id: int,
        title: str | None = None,
        department: str | None = None,
        ects: int | None = None,
        description: str | None = None,
    ) -> CourseListItem:
        course = await self.repository.get_course_by_id(course_id)
        if not course:
            raise ValueError(f"Course {course_id} not found")

        update_data = {}
        if title is not None:
            update_data["title"] = title
        if department is not None:
            update_data["department"] = department
        if ects is not None:
            update_data["ects"] = ects
        if description is not None:
            update_data["description"] = description

        updated = await self.repository.update_course(course, **update_data)
        return CourseListItem.model_validate(updated)

    async def _check_db_connection(self) -> bool:
        try:
            await self.repository.get_total_users_count()
            return True
        except exc.SQLAlchemyError:
            return False

    async def _check_redis_connection(self) -> bool:
        try:
            await self.redis.ping()
            return True
        except Exception:
            return False
