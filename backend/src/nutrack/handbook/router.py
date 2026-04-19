from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from nutrack.auth.dependencies import get_current_user
from nutrack.handbook.dependencies import get_handbook_service
from nutrack.handbook.schemas import HandbookStatusResponse, HandbookUploadResponse
from nutrack.handbook.service import HandbookService
from nutrack.users.models import User
from nutrack.utils import ApiResponse

router = APIRouter(prefix="/handbook", tags=["handbook"])

_MAX_PDF_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post(
    "/upload",
    response_model=ApiResponse[HandbookUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_handbook(
    enrollment_year: int = Form(..., ge=2010, le=2030),
    file: UploadFile = File(...),
    _user: User = Depends(get_current_user),
    service: HandbookService = Depends(get_handbook_service),
):
    """
    Upload an Academic Handbook PDF for a specific enrollment year.
    The PDF is parsed with AI and the requirements are stored.
    If a plan already exists for that year it is replaced.
    """
    if file.content_type not in ("application/pdf", "application/octet-stream"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are accepted.",
        )
    pdf_bytes = await file.read()
    if len(pdf_bytes) > _MAX_PDF_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds 20 MB limit.",
        )
    result = await service.upload_and_parse(
        enrollment_year=enrollment_year,
        filename=file.filename or f"handbook_{enrollment_year}.pdf",
        pdf_bytes=pdf_bytes,
    )
    return ApiResponse(data=result)


@router.post(
    "/upload-json",
    response_model=ApiResponse[HandbookUploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload_handbook_json(
    enrollment_year: int = Form(..., ge=2010, le=2030),
    file: UploadFile = File(...),
    _user: User = Depends(get_current_user),
    service: HandbookService = Depends(get_handbook_service),
):
    """
    Upload a JSON file containing degree plan requirements for a specific enrollment year.
    Supports SEDS/SSH wrapper format with underscore-separated major keys.
    No OpenAI required — parsed directly.
    """
    if file.content_type not in (
        "application/json",
        "text/plain",
        "application/octet-stream",
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JSON files are accepted.",
        )
    json_bytes = await file.read()
    result = await service.upload_json(
        enrollment_year=enrollment_year,
        filename=file.filename or f"handbook_{enrollment_year}.json",
        json_bytes=json_bytes,
    )
    return ApiResponse(data=result)


@router.get(
    "/{enrollment_year}",
    response_model=ApiResponse[HandbookStatusResponse],
)
async def get_handbook_status(
    enrollment_year: int,
    _user: User = Depends(get_current_user),
    service: HandbookService = Depends(get_handbook_service),
):
    """Check the status of a parsed handbook for a given enrollment year."""
    result = await service.get_status(enrollment_year)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No handbook found for enrollment year {enrollment_year}.",
        )
    return ApiResponse(data=result)
