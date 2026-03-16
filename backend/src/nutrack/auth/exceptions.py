from nutrack.exceptions import AppException


class OAuthError(AppException):
    def __init__(self, message: str = "OAuth authentication failed") -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="OAUTH_ERROR",
        )


class InvalidEmailDomainError(AppException):
    def __init__(
        self,
        message: str = "Only @nu.edu.kz email domain is allowed",
    ) -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="INVALID_EMAIL_DOMAIN",
        )


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Invalid or expired token") -> None:
        super().__init__(
            message=message,
            status_code=401,
            error_code="INVALID_TOKEN",
        )
