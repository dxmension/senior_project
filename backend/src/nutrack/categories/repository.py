from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.categories.models import Category
from nutrack.database import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Category)

    async def get_all_by_user(self, user_id: int) -> list[Category]:
        stmt = (
            select(Category)
            .where(Category.user_id == user_id)
            .order_by(Category.name.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_and_user(
        self, category_id: int, user_id: int
    ) -> Category | None:
        stmt = select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_and_user(self, name: str, user_id: int) -> Category | None:
        stmt = select(Category).where(
            Category.name == name,
            Category.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id_and_user(self, category_id: int, user_id: int) -> bool:
        category = await self.get_by_id_and_user(category_id, user_id)
        if not category:
            return False
        await self.session.delete(category)
        await self.session.flush()
        return True
