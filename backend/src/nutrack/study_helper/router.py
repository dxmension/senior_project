from fastapi import APIRouter, Depends, Query, status

from nutrack.auth.dependencies import get_current_user
from nutrack.study_helper.dependencies import get_study_helper_service
from nutrack.study_helper.schemas import (
    DeepDiveResponse,
    DetailResponse,
    GenerateRequest,
    StudyGuideResponse,
    TopicListResponse,
    WeekOverviewResponse,
)
from nutrack.study_helper.service import StudyHelperService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/study-helper", tags=["study-helper"])


@router.post(
    "/{course_id}/warm",
    response_model=ApiResponse[list[int]],
)
async def warm_cache(
    course_id: int,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[list[int]]:
    refreshed = await service.warm_cache(user.id, course_id)
    return ApiResponse(data=refreshed)


@router.post(
    "/{course_id}/week/{week}",
    response_model=ApiResponse[WeekOverviewResponse],
)
async def generate_week_overview(
    course_id: int,
    week: int,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[WeekOverviewResponse]:
    result = await service.generate_week_overview(user.id, course_id, week)
    return ApiResponse(data=result)


@router.get(
    "/{course_id}/week/{week}/topics",
    response_model=ApiResponse[TopicListResponse],
)
async def list_topics(
    course_id: int,
    week: int,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[TopicListResponse]:
    result = await service.list_topics(user.id, course_id, week)
    return ApiResponse(data=result)


@router.post(
    "/{course_id}/generate",
    response_model=ApiResponse[StudyGuideResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_overview(
    course_id: int,
    body: GenerateRequest,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[StudyGuideResponse]:
    result = await service.generate_overview(
        user.id, course_id, body.topic, body.week
    )
    return ApiResponse(data=result)


@router.get(
    "/{course_id}/guides/{guide_id}",
    response_model=ApiResponse[StudyGuideResponse],
)
async def get_guide(
    guide_id: int,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[StudyGuideResponse]:
    result = await service.get_guide(user.id, guide_id)
    return ApiResponse(data=result)


@router.post(
    "/{course_id}/guides/{guide_id}/detail/{point_id}",
    response_model=ApiResponse[DetailResponse],
)
async def generate_detail(
    guide_id: int,
    point_id: str,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[DetailResponse]:
    result = await service.generate_detail(user.id, guide_id, point_id)
    return ApiResponse(data=result)


@router.post(
    "/{course_id}/guides/{guide_id}/deep/{point_id}",
    response_model=ApiResponse[DeepDiveResponse],
)
async def generate_deep_dive(
    guide_id: int,
    point_id: str,
    dive_type: str = Query(..., pattern="^(explain_more|give_example)$"),
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[DeepDiveResponse]:
    result = await service.generate_deep_dive(
        user.id, guide_id, point_id, dive_type
    )
    return ApiResponse(data=result)


@router.delete(
    "/{course_id}/guides/{guide_id}",
    response_model=ApiResponse[None],
)
async def delete_guide(
    course_id: int,
    guide_id: int,
    user: User = Depends(get_current_user),
    service: StudyHelperService = Depends(get_study_helper_service),
) -> ApiResponse[None]:
    await service.delete_guide(user.id, course_id, guide_id)
    return ApiResponse(data=None)
