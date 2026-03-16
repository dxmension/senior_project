from fastapi import APIRouter, Depends, File, UploadFile

from nutrack.auth.dependencies import get_current_user
from nutrack.shared.api.response import ApiResponse
from nutrack.transcripts.dependencies import get_transcript_service
from nutrack.users.models import User
from nutrack.transcripts.schemas import (
    ManualTranscriptRequest,
    TranscriptUploadResponse,
    TranscriptUploadStatusResponse,
)
from nutrack.transcripts.service import TranscriptService

router = APIRouter(prefix="/transcripts", tags=["transcripts"])


@router.post("/uploads", response_model=ApiResponse[TranscriptUploadResponse])
async def upload_transcript(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    upload_id = await service.upload(user.id, file)
    response = TranscriptUploadResponse(upload_id=upload_id, status="completed")
    return ApiResponse(data=response)


@router.get(
    "/uploads/{upload_id}",
    response_model=ApiResponse[TranscriptUploadStatusResponse],
)
async def get_upload_status(
    upload_id: str,
    service: TranscriptService = Depends(get_transcript_service),
):
    status = await service.get_upload_status(upload_id)
    return ApiResponse(data=TranscriptUploadStatusResponse(**status))


@router.post("/manual", response_model=ApiResponse)
async def save_manual_transcript(
    body: ManualTranscriptRequest,
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    await service.save_manual_entries(user.id, body.model_dump())
    return ApiResponse(data={"saved": True})


@router.post("/confirm", response_model=ApiResponse)
async def confirm_transcript(
    body: ManualTranscriptRequest,
    user: User = Depends(get_current_user),
    service: TranscriptService = Depends(get_transcript_service),
):
    await service.save_manual_entries(user.id, body.model_dump())
    return ApiResponse(data={"confirmed": True})
