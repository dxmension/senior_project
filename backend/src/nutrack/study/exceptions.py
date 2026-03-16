from nutrack.exceptions import AppException


class StudyFeatureNotImplementedError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Study feature is not implemented yet",
            status_code=501,
            error_code="STUDY_NOT_IMPLEMENTED",
        )
