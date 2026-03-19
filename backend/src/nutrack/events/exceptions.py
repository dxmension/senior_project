from nutrack.exceptions import AppException


class EventNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Event not found",
            status_code=404,
            error_code="EVENT_NOT_FOUND",
        )


class EventCategoryNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Category not found or does not belong to you",
            status_code=404,
            error_code="EVENT_CATEGORY_NOT_FOUND",
        )
