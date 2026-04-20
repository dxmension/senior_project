from nutrack.exceptions import AppException


class MindmapGenerationError(AppException):
    def __init__(self, detail: str = "Mindmap generation failed") -> None:
        super().__init__(
            message=detail,
            status_code=503,
            error_code="MINDMAP_GENERATION_FAILED",
        )


class MindmapUnavailableError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Mindmap generation unavailable: OpenAI API key not configured",
            status_code=503,
            error_code="MINDMAP_UNAVAILABLE",
        )


class MindmapNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Mindmap not found",
            status_code=404,
            error_code="MINDMAP_NOT_FOUND",
        )
