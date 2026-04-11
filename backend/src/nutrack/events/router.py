from datetime import datetime

from fastapi import APIRouter, Depends, Query, status

from nutrack.auth.dependencies import get_current_user
from nutrack.events.dependencies import get_event_service
from nutrack.events.schemas import CreateEventRequest, EventResponse, UpdateEventRequest
from nutrack.events.service import EventService
from nutrack.utils import ApiResponse
from nutrack.users.models import User

router = APIRouter(tags=["events"])


@router.get("", response_model=ApiResponse[list[EventResponse]])
async def list_events(
    from_dt: datetime = Query(...),
    to_dt: datetime = Query(...),
    user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    events = await service.list_events(user.id, from_dt, to_dt)
    return ApiResponse(data=events)


@router.post(
    "",
    response_model=ApiResponse[EventResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
    body: CreateEventRequest,
    user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    event = await service.create_event(user.id, body)
    return ApiResponse(data=event)


@router.get("/{event_id}", response_model=ApiResponse[EventResponse])
async def get_event(
    event_id: int,
    user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    event = await service.get_event(user.id, event_id)
    return ApiResponse(data=event)


@router.patch("/{event_id}", response_model=ApiResponse[EventResponse])
async def update_event(
    event_id: int,
    body: UpdateEventRequest,
    user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    event = await service.update_event(user.id, event_id, body)
    return ApiResponse(data=event)


@router.delete("/{event_id}", response_model=ApiResponse[None])
async def delete_event(
    event_id: int,
    user: User = Depends(get_current_user),
    service: EventService = Depends(get_event_service),
):
    await service.delete_event(user.id, event_id)
    return ApiResponse(data=None)
