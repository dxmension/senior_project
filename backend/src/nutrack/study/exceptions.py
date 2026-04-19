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


class MockExamError(AppException):
    pass


class MockExamValidationError(MockExamError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=400,
            error_code="MOCK_EXAM_INVALID",
        )


class MockExamForbiddenError(MockExamError):
    def __init__(self, message: str = "You do not have access to this mock exam") -> None:
        super().__init__(
            message=message,
            status_code=403,
            error_code="MOCK_EXAM_FORBIDDEN",
        )


class MockExamNotFoundError(MockExamError):
    def __init__(self) -> None:
        super().__init__(
            message="Mock exam not found",
            status_code=404,
            error_code="MOCK_EXAM_NOT_FOUND",
        )


class MockExamAttemptNotFoundError(MockExamError):
    def __init__(self) -> None:
        super().__init__(
            message="Mock exam attempt not found",
            status_code=404,
            error_code="MOCK_EXAM_ATTEMPT_NOT_FOUND",
        )


class MockExamQuestionNotFoundError(MockExamError):
    def __init__(self) -> None:
        super().__init__(
            message="Mock exam question not found",
            status_code=404,
            error_code="MOCK_EXAM_QUESTION_NOT_FOUND",
        )
