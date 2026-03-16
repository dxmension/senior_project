from nutrack.exceptions import AppException


class NotificationsFeatureNotImplementedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Notifications feature is not implemented yet",
            status_code=501,
            error_code="NOTIFICATIONS_NOT_IMPLEMENTED",
        )
