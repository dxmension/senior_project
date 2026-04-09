from typing import Any

from nutrack.exceptions import AppException


class CourseCatalogFileError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_CATALOG_FILE_ERROR",
        )


class CourseNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Course not found",
            status_code=404,
            error_code="COURSE_NOT_FOUND",
        )


class CourseSearchError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_SEARCH_ERROR",
        )


class CourseScheduleFileError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_SCHEDULE_FILE_ERROR",
        )


class CourseGpaStatsFileError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_GPA_STATS_FILE_ERROR",
        )


class CourseGpaStatsParsingError(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(
            message=message,
            status_code=422,
            error_code="COURSE_GPA_STATS_PARSE_ERROR",
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
