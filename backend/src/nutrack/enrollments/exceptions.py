from nutrack.exceptions import AppException


class EnrollmentConflictError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Enrollment already exists for the current term and year",
            status_code=409,
            error_code="ENROLLMENT_CONFLICT",
        )


class EnrollmentNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Enrollment not found",
            status_code=404,
            error_code="ENROLLMENT_NOT_FOUND",
        )
