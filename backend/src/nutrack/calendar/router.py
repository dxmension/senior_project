from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status

from nutrack.auth.dependencies import get_current_user
from nutrack.calendar.dependencies import get_calendar_service
from nutrack.calendar.schemas import CalendarEntry
from nutrack.calendar.service import CalendarService
from nutrack.shared.api.response import ApiResponse
from nutrack.users.models import User

router = APIRouter(tags=["calendar"])

MAX_CALENDAR_RANGE_DAYS = 90


@router.get("", response_model=ApiResponse[list[CalendarEntry]])
async def get_calendar(
    from_dt: datetime = Query(...),
    to_dt: datetime = Query(...),
    user: User = Depends(get_current_user),
    service: CalendarService = Depends(get_calendar_service),
):
    if to_dt <= from_dt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="to_dt must be after from_dt",
        )
    if (to_dt - from_dt) > timedelta(days=MAX_CALENDAR_RANGE_DAYS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Calendar range must not exceed {MAX_CALENDAR_RANGE_DAYS} days",
        )
    entries = await service.get_calendar(user.id, from_dt, to_dt)
    return ApiResponse(data=entries)
