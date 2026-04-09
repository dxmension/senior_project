from nutrack.exceptions import AppException


class AssessmentNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Assessment not found",
            status_code=404,
            error_code="ASSESSMENT_NOT_FOUND",
        )


class AssessmentNotEnrolledError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="You must be enrolled in this course to add assessments",
            status_code=403,
            error_code="ASSESSMENT_NOT_ENROLLED",
        )
