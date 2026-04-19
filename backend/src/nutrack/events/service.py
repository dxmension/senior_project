import calendar
from datetime import datetime, timedelta

from nutrack.events.exceptions import (
    CategoryNameConflictError,
    CategoryNotFoundError,
    EventCategoryNotFoundError,
    EventNotFoundError,
)
from nutrack.events.models import Category, Event, RecurrenceType
from nutrack.events.repository import CategoryRepository, EventRepository
from nutrack.events.schemas import (
    CategoryResponse,
    CreateCategoryRequest,
    CreateEventRequest,
    EventResponse,
    UpdateCategoryRequest,
    UpdateEventRequest,
)


def _add_months(dt: datetime, n: int) -> datetime:
    month = dt.month - 1 + n
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def _next_occurrence(dt: datetime, recurrence: RecurrenceType) -> datetime:
    if recurrence == RecurrenceType.DAILY:
        return dt + timedelta(days=1)
    if recurrence == RecurrenceType.WEEKLY:
        return dt + timedelta(weeks=1)
    if recurrence == RecurrenceType.BIWEEKLY:
        return dt + timedelta(weeks=2)
    if recurrence == RecurrenceType.MONTHLY:
        return _add_months(dt, 1)
    return dt


def _category_response(category: Category | None) -> CategoryResponse | None:
    if category is None:
        return None
    return CategoryResponse(
        id=category.id,
        name=category.name,
        color=category.color,
        created_at=category.created_at,
        updated_at=category.updated_at,
    )


class EventCategoryService:
    def __init__(self, repo: CategoryRepository) -> None:
        self.repo = repo

    async def list_categories(self, user_id: int) -> list[CategoryResponse]:
        categories = await self.repo.get_all_by_user(user_id)
        return [_category_response(category) for category in categories]

    async def create_category(
        self,
        user_id: int,
        data: CreateCategoryRequest,
    ) -> CategoryResponse:
        existing = await self.repo.get_by_name_and_user(data.name, user_id)
        if existing:
            raise CategoryNameConflictError()
        category = await self.repo.create(
            user_id=user_id,
            name=data.name,
            color=data.color,
        )
        return _category_response(category)

    async def update_category(
        self,
        user_id: int,
        category_id: int,
        data: UpdateCategoryRequest,
    ) -> CategoryResponse:
        category = await self.repo.get_by_id_and_user(category_id, user_id)
        if not category:
            raise CategoryNotFoundError()
        if data.name is not None and data.name != category.name:
            conflict = await self.repo.get_by_name_and_user(data.name, user_id)
            if conflict:
                raise CategoryNameConflictError()
        updates = {field: getattr(data, field) for field in data.model_fields_set}
        if updates:
            await self.repo.update(category, **updates)
        return _category_response(category)

    async def delete_category(self, user_id: int, category_id: int) -> None:
        deleted = await self.repo.delete_by_id_and_user(category_id, user_id)
        if not deleted:
            raise CategoryNotFoundError()


def _build_response(
    event: Event,
    start_at: datetime | None = None,
    end_at: datetime | None = None,
) -> EventResponse:
    effective_start = start_at if start_at is not None else event.start_at
    effective_end = end_at if end_at is not None else event.end_at
    return EventResponse(
        id=event.id,
        title=event.title,
        description=event.description,
        start_at=effective_start,
        end_at=effective_end,
        is_all_day=event.is_all_day,
        location=event.location,
        recurrence=event.recurrence,
        recurrence_end_at=event.recurrence_end_at,
        category=_category_response(event.category),
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


def _expand_event(
    event: Event, from_dt: datetime, to_dt: datetime
) -> list[EventResponse]:
    if event.recurrence == RecurrenceType.NONE:
        if from_dt <= event.start_at <= to_dt:
            return [_build_response(event)]
        return []

    duration = (event.end_at - event.start_at) if event.end_at else None
    end_bound = min(to_dt, event.recurrence_end_at or to_dt)
    occurrences: list[EventResponse] = []
    current = event.start_at

    while current <= end_bound:
        if current >= from_dt:
            virtual_end = (current + duration) if duration else None
            occurrences.append(_build_response(event, current, virtual_end))
        current = _next_occurrence(current, event.recurrence)

    return occurrences


class EventService:
    def __init__(
        self,
        event_repo: EventRepository,
        category_repo: CategoryRepository,
    ) -> None:
        self.event_repo = event_repo
        self.category_repo = category_repo

    async def list_events(
        self,
        user_id: int,
        from_dt: datetime,
        to_dt: datetime,
    ) -> list[EventResponse]:
        events = await self.event_repo.get_by_user_in_range(user_id, from_dt, to_dt)
        result: list[EventResponse] = []
        for event in events:
            result.extend(_expand_event(event, from_dt, to_dt))
        result.sort(key=lambda e: e.start_at)
        return result

    async def create_event(
        self, user_id: int, data: CreateEventRequest
    ) -> EventResponse:
        if data.category_id is not None:
            await self._verify_category(user_id, data.category_id)
        event = await self.event_repo.create(
            user_id=user_id,
            category_id=data.category_id,
            title=data.title,
            description=data.description,
            start_at=data.start_at,
            end_at=data.end_at,
            is_all_day=data.is_all_day,
            location=data.location,
            recurrence=data.recurrence,
            recurrence_end_at=data.recurrence_end_at,
        )
        loaded = await self.event_repo.get_by_id_and_user(event.id, user_id)
        return _build_response(loaded)

    async def get_event(self, user_id: int, event_id: int) -> EventResponse:
        event = await self.event_repo.get_by_id_and_user(event_id, user_id)
        if not event:
            raise EventNotFoundError()
        return _build_response(event)

    async def update_event(
        self, user_id: int, event_id: int, data: UpdateEventRequest
    ) -> EventResponse:
        event = await self.event_repo.get_by_id_and_user(event_id, user_id)
        if not event:
            raise EventNotFoundError()
        if "category_id" in data.model_fields_set and data.category_id is not None:
            await self._verify_category(user_id, data.category_id)
        updates = {field: getattr(data, field) for field in data.model_fields_set}
        if updates:
            await self.event_repo.update(event, **updates)
        return _build_response(event)

    async def delete_event(self, user_id: int, event_id: int) -> None:
        deleted = await self.event_repo.delete_by_id_and_user(event_id, user_id)
        if not deleted:
            raise EventNotFoundError()

    async def _verify_category(self, user_id: int, category_id: int) -> None:
        category = await self.category_repo.get_by_id_and_user(category_id, user_id)
        if not category:
            raise EventCategoryNotFoundError()
