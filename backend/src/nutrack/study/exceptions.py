from nutrack.exceptions import AppException


class StudyMaterialError(AppException):
    pass


class StudyMaterialValidationError(StudyMaterialError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="STUDY_MATERIAL_INVALID",
        )


class StudyMaterialForbiddenError(StudyMaterialError):
    def __init__(self, message: str = "You are not enrolled in this course") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="STUDY_MATERIAL_FORBIDDEN",
        )


class StudyMaterialNotFoundError(StudyMaterialError):
    def __init__(self) -> None:
        super().__init__(
            message="Study material not found",
            status_code=404,
            error_code="STUDY_MATERIAL_NOT_FOUND",
        )


class StudyMaterialQueueError(StudyMaterialError):
    def __init__(self) -> None:
        super().__init__(
            message="Failed to queue material upload",
            status_code=500,
            error_code="STUDY_MATERIAL_QUEUE_FAILED",
        )
