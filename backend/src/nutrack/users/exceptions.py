from nutrack.exceptions import AppException


class NotFoundError(AppException):
    def __init__(self, entity: str = "Resource") -> None:
        super().__init__(
            message=f"{entity} not found",
            status_code=404,
            error_code="NOT_FOUND",
        )


class ForbiddenError(AppException):
    def __init__(self, message: str = "Access denied") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
        )
