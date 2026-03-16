from typing import Any

from nutrack.exceptions import AppException


class CourseScheduleFileError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_SCHEDULE_FILE_ERROR",
        )


class CourseScheduleParsingError(AppException):
    def __init__(
        self,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_SCHEDULE_PARSE_ERROR",
            details=details,
        )
