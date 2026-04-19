from fastapi import APIRouter, Depends, status

from nutrack.auth.dependencies import get_current_user
from nutrack.mindmaps.dependencies import get_mindmap_service
from nutrack.mindmaps.schemas import GenerateMindmapRequest, SavedMindmapResponse
from nutrack.mindmaps.service import MindmapService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/mindmaps", tags=["mindmaps"])


@router.get("/{course_id}", response_model=ApiResponse[list[SavedMindmapResponse]])
async def list_mindmaps(
    course_id: int,
    user: User = Depends(get_current_user),
    service: MindmapService = Depends(get_mindmap_service),
) -> ApiResponse[list[SavedMindmapResponse]]:
    mindmaps = await service.list_for_course(user.id, course_id)
    return ApiResponse(data=mindmaps)


@router.post(
    "/{course_id}/generate",
    response_model=ApiResponse[SavedMindmapResponse],
    status_code=status.HTTP_201_CREATED,
)
async def generate_mindmap(
    course_id: int,
    body: GenerateMindmapRequest,
    user: User = Depends(get_current_user),
    service: MindmapService = Depends(get_mindmap_service),
) -> ApiResponse[SavedMindmapResponse]:
    mindmap = await service.generate_and_save(user.id, course_id, body)
    return ApiResponse(data=mindmap)


@router.delete(
    "/{course_id}/{mindmap_id}",
    response_model=ApiResponse[None],
)
async def delete_mindmap(
    course_id: int,
    mindmap_id: int,
    user: User = Depends(get_current_user),
    service: MindmapService = Depends(get_mindmap_service),
) -> ApiResponse[None]:
    await service.delete(user.id, course_id, mindmap_id)
    return ApiResponse(data=None)
