from fastapi import APIRouter, Depends

from nutrack.auth.dependencies import get_current_user
from nutrack.flashcards.dependencies import get_flashcards_service
from nutrack.flashcards.schemas import FlashcardItem
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/flashcards", tags=["flashcards"])


@router.get(
    "/mock-exams/{mock_exam_id}",
    response_model=ApiResponse[list[FlashcardItem]],
)
async def get_mock_exam_flashcards(
    mock_exam_id: int,
    user: User = Depends(get_current_user),
    service = Depends(get_flashcards_service),
):
    flashcards = await service.get_mock_exam_flashcards(user.id, mock_exam_id)
    return ApiResponse(data=flashcards)
