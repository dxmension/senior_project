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


class EnrollmentEligibilityError(AppException):
    def __init__(self, reason: str) -> None:
        super().__init__(
            message=reason,
            status_code=400,
            error_code="ENROLLMENT_ELIGIBILITY",
        )


class EnrollmentCreditsExceededError(AppException):
    def __init__(self, current: int, adding: int, cap: int) -> None:
        super().__init__(
            message=f"Enrolling would bring total to {current + adding} ECTS (cap {cap}).",
            status_code=400,
            error_code="ENROLLMENT_CREDITS_EXCEEDED",
        )
        self.current = current
        self.adding = adding
        self.cap = cap


class EnrollmentScheduleConflictError(AppException):
    def __init__(self, other_code: str) -> None:
        super().__init__(
            message=f"Schedule conflicts with {other_code}.",
            status_code=409,
            error_code="ENROLLMENT_SCHEDULE_CONFLICT",
        )
        self.other_code = other_code
