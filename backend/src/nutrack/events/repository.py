from datetime import datetime

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from nutrack.database import BaseRepository
from nutrack.events.models import Category, Event, RecurrenceType


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
        self,
        category_id: int,
        user_id: int,
    ) -> Category | None:
        stmt = select(Category).where(
            Category.id == category_id,
            Category.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_name_and_user(
        self,
        name: str,
        user_id: int,
    ) -> Category | None:
        stmt = select(Category).where(
            Category.name == name,
            Category.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id_and_user(
        self,
        category_id: int,
        user_id: int,
    ) -> bool:
        category = await self.get_by_id_and_user(category_id, user_id)
        if not category:
            return False
        await self.session.delete(category)
        await self.session.flush()
        return True


class EventRepository(BaseRepository[Event]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Event)

    async def get_by_user_in_range(
        self,
        user_id: int,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[Event]:
        """
        Returns non-recurring events that start within [from_dt, to_dt],
        plus recurring events that may have occurrences overlapping the range.
        """
        stmt = (
            select(Event)
            .options(joinedload(Event.category))
            .where(
                Event.user_id == user_id,
                Event.start_at <= to_dt,
                or_(
                    # Non-recurring: start within range
                    and_(
                        Event.recurrence == RecurrenceType.NONE,
                        Event.start_at >= from_dt,
                    ),
                    # Recurring: started before end of range AND recurrence extends into range
                    and_(
                        Event.recurrence != RecurrenceType.NONE,
                        or_(
                            Event.recurrence_end_at.is_(None),
                            Event.recurrence_end_at >= from_dt,
                        ),
                    ),
                ),
            )
            .order_by(Event.start_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_id_and_user(
        self, event_id: int, user_id: int
    ) -> Event | None:
        stmt = (
            select(Event)
            .options(joinedload(Event.category))
            .where(Event.id == event_id, Event.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_by_id_and_user(self, event_id: int, user_id: int) -> bool:
        event = await self.get_by_id_and_user(event_id, user_id)
        if not event:
            return False
        await self.session.delete(event)
        await self.session.flush()
        return True
