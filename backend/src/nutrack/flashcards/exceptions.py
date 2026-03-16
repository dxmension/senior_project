from nutrack.exceptions import AppException


class FlashcardsFeatureNotImplementedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Flashcards feature is not implemented yet",
            status_code=501,
            error_code="FLASHCARDS_NOT_IMPLEMENTED",
        )
