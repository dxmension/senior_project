from nutrack.exceptions import AppException


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
