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


class ReviewNotFoundError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Review not found",
            status_code=404,
            error_code="REVIEW_NOT_FOUND",
        )


class ReviewAlreadyExistsError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="You have already reviewed this course",
            status_code=409,
            error_code="REVIEW_ALREADY_EXISTS",
        )


class ReviewForbiddenError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="You can only modify your own reviews",
            status_code=403,
            error_code="REVIEW_FORBIDDEN",
        )


class ReviewInappropriateContentError(AppException):
    def __init__(self) -> None:
        super().__init__(
            message="Your review contains inappropriate language. Please revise your comment.",
            status_code=422,
            error_code="REVIEW_INAPPROPRIATE_CONTENT",
        )
