from nutrack.exceptions import AppException


class FlashcardDeckNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Flashcard deck not found",
            status_code=404,
            error_code="FLASHCARD_DECK_NOT_FOUND",
        )


class FlashcardSessionNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Flashcard session not found",
            status_code=404,
            error_code="FLASHCARD_SESSION_NOT_FOUND",
        )


class FlashcardSessionAlreadyCompletedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Flashcard session is already completed",
            status_code=409,
            error_code="FLASHCARD_SESSION_COMPLETED",
        )


class FlashcardNoMaterialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="No course materials available for flashcard generation",
            status_code=422,
            error_code="FLASHCARD_NO_MATERIALS",
        )
