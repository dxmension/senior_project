from nutrack.exceptions import AppException


class StudyGuideGenerationError(AppException):
    def __init__(self, detail: str = "Study guide generation failed") -> None:
        super().__init__(
            message=detail,
            status_code=503,
            error_code="STUDY_GUIDE_GENERATION_FAILED",
        )


class StudyGuideUnavailableError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Study guide generation unavailable: OpenAI API key not configured",
            status_code=503,
            error_code="STUDY_GUIDE_UNAVAILABLE",
        )


class StudyGuideNoMaterialsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Study guide generation requires course materials",
            status_code=422,
            error_code="STUDY_GUIDE_NO_MATERIALS",
        )


class StudyGuideNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Study guide not found",
            status_code=404,
            error_code="STUDY_GUIDE_NOT_FOUND",
        )
