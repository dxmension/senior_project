from nutrack.exceptions import AppException


class UserNotFoundError(AppException):
    def __init__(self, user_id: int):
        super().__init__(
            message=f"User with ID {user_id} not found",
            status_code=404,
            error_code="USER_NOT_FOUND",
        )


class CannotModifySelfError(AppException):
    def __init__(self):
        super().__init__(
            message="Cannot modify your own admin status",
            status_code=400,
            error_code="CANNOT_MODIFY_SELF",
        )
