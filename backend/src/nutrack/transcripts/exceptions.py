from nutrack.exceptions import AppException


class FileValidationError(AppException):
    def __init__(self, message: str = "Invalid file") -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="FILE_VALIDATION_ERROR",
        )


class TranscriptParsingError(AppException):
    def __init__(self, message: str = "Failed to parse transcript") -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="TRANSCRIPT_PARSE_ERROR",
        )


class TranscriptUploadNotFoundError(AppException):
    def __init__(self, upload_id: str) -> None:
        super().__init__(
            message=f"Transcript upload {upload_id} not found",
            status_code=404,
            error_code="TRANSCRIPT_UPLOAD_NOT_FOUND",
        )
