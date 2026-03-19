from nutrack.exceptions import AppException


class AISummaryUnavailableError(AppException):
    def __init__(self, reason: str = "") -> None:
        super().__init__(
            message="AI summary is temporarily unavailable",
            status_code=503,
            error_code="AI_SUMMARY_UNAVAILABLE",
        )
        self.reason = reason
