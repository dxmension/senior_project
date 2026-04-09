from nutrack.exceptions import AppException


class CategoryNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Category not found",
            status_code=404,
            error_code="CATEGORY_NOT_FOUND",
        )


class CategoryNameConflictError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Category with this name already exists",
            status_code=409,
            error_code="CATEGORY_NAME_CONFLICT",
        )
