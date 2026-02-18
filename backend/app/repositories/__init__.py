from app.repositories.base import BaseRepository
from app.repositories.user import UserRepository
from app.repositories.transcript import TranscriptRepository
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository

__all__ = [
    "BaseRepository",
    "UserRepository",
    "TranscriptRepository",
    "CourseRepository",
    "EnrollmentRepository",
]
