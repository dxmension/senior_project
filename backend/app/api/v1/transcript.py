from fastapi import APIRouter, Depends, UploadFile, File

from app.dependencies import get_current_user, get_transcript_service
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.transcript import (
    ManualTranscriptRequest,
    ParsedTranscriptData,
    TranscriptConfirmRequest,
    TranscriptStatusResponse,
)
from app.services.transcript import TranscriptService

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("/upload", response_model=ApiResponse[TranscriptStatusResponse])
async def upload_transcript(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    result = await service.upload(user.id, file)
    return ApiResponse(data=result)


@router.get("/status", response_model=ApiResponse[TranscriptStatusResponse])
async def get_transcript_status(
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    result = await service.get_status(user.id)
    return ApiResponse(data=result)


@router.post("/confirm", response_model=ApiResponse)
async def confirm_transcript(
    body: TranscriptConfirmRequest,
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    data = ParsedTranscriptData(major=body.major, courses=body.courses)
    await service.confirm(user.id, data)
    return ApiResponse(message="Transcript confirmed successfully")


@router.post("/manual", response_model=ApiResponse)
async def manual_entry(
    body: ManualTranscriptRequest,
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    data = ParsedTranscriptData(major=body.major, courses=body.courses)
    await service.manual_entry(user.id, data)
    return ApiResponse(message="Manual entry saved successfully")
