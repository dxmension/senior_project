from app.exceptions.base import AppException


class NotFoundError(AppException):
    def __init__(self, entity: str = "Resource") -> None:
        super().__init__(
            message=f"{entity} not found", status_code=404, error_code="NOT_FOUND",
        )


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated") -> None:
        super().__init__(
            message=message, status_code=401, error_code="UNAUTHORIZED",
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(
            message=message, status_code=403, error_code="FORBIDDEN",
        )


class InvalidEmailDomainError(AppException):
    def __init__(
        self, message: str = "Only @nu.edu.kz email domain is allowed"
    ) -> None:
        super().__init__(
            message=message, status_code=403, error_code="INVALID_EMAIL_DOMAIN",
        )


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(
            message=message, status_code=401, error_code="INVALID_TOKEN",
        )


class OAuthError(AppException):
    def __init__(self, message: str = "OAuth authentication failed") -> None:
        super().__init__(
            message=message, status_code=400, error_code="OAUTH_ERROR",
        )


class FileValidationError(AppException):
    def __init__(self, message: str = "Invalid file") -> None:
        super().__init__(
            message=message, status_code=422, error_code="FILE_VALIDATION_ERROR",
        )


class TranscriptParsingError(AppException):
    def __init__(self, message: str = "Failed to parse transcript") -> None:
        super().__init__(
            message=message, status_code=422, error_code="TRANSCRIPT_PARSE_ERROR",
        )


class RateLimitError(AppException):
    def __init__(self, message: str = "Too many requests") -> None:
        super().__init__(
            message=message, status_code=429, error_code="RATE_LIMITED",
        )
