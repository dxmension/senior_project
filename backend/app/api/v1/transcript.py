from fastapi import APIRouter, Depends, UploadFile, File

from app.dependencies import get_current_user, get_transcript_service
from app.models.user import User
from app.schemas.common import ApiResponse

from app.services.transcript import TranscriptService

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("/upload", response_model=ApiResponse)
async def upload_transcript(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    await service.upload(user.id, file)
    return ApiResponse()
