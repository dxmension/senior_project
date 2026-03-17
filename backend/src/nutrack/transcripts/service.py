import logging
from datetime import datetime, timezone
import re
from uuid import uuid4

from fastapi import UploadFile
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.transcripts.exceptions import (
    FileValidationError,
    TranscriptParsingError,
    TranscriptUploadNotFoundError,
)
from nutrack.transcripts.parser import (
    get_enrollment_status,
    parse_transcript_from_bytes,
)
from nutrack.transcripts.repository import (
    CourseRepository,
    EnrollmentRepository,
)
from nutrack.users.repository import UserRepository
from nutrack.semester import normalize_term

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
UPLOAD_KEY_PREFIX = "transcript_upload:"
logger = logging.getLogger(__name__)


class TranscriptService:
    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        self.session = session
        self.redis = redis
        self.course_repo = CourseRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.user_repo = UserRepository(session)

    async def _set_upload_status(
        self,
        upload_id: str,
        status: str,
        error: str | None = None,
    ) -> None:
        key = f"{UPLOAD_KEY_PREFIX}{upload_id}"
        payload = {
            "upload_id": upload_id,
            "status": status,
            "error": error or "",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        await self.redis.hset(key, mapping=payload)
        await self.redis.expire(key, 86400)

    async def get_upload_status(self, upload_id: str) -> dict:
        key = f"{UPLOAD_KEY_PREFIX}{upload_id}"
        payload = await self.redis.hgetall(key)
        if not payload:
            raise TranscriptUploadNotFoundError(upload_id)

        return {
            "upload_id": payload["upload_id"],
            "status": payload["status"],
            "error": payload.get("error") or None,
        }

    async def upload(self, user_id: int, file: UploadFile) -> str:
        upload_id = str(uuid4())
        await self._set_upload_status(upload_id, "processing")
        try:
            if file.content_type != "application/pdf":
                await self._set_upload_status(
                    upload_id,
                    "failed",
                    "Only PDF files are accepted",
                )
                raise FileValidationError("Only PDF files are accepted")

            content = await file.read()
            if len(content) > MAX_FILE_SIZE:
                await self._set_upload_status(
                    upload_id,
                    "failed",
                    "File size exceeds 10MB limit",
                )
                raise FileValidationError("File size exceeds 10MB limit")

            student_info = parse_transcript_from_bytes(content)
            if not student_info or not student_info.get("courses"):
                await self._set_upload_status(
                    upload_id,
                    "failed",
                    "Failed to parse transcript, please try again later",
                )
                raise TranscriptParsingError(
                    "Failed to parse transcript, please try again later"
                )

            student_name = (student_info.get("student_name") or "").split()
            if len(student_name) < 2:
                await self._set_upload_status(
                    upload_id,
                    "failed",
                    "Invalid student name in transcript",
                )
                raise FileValidationError("Invalid student name in transcript")

            first_name, last_name = student_name[1], student_name[0]
            user = await self.user_repo.get_by_name(first_name, last_name)
            if not user or user.id != user_id:
                await self._set_upload_status(
                    upload_id,
                    "failed",
                    "You uploaded not your own transcript",
                )
                raise FileValidationError(
                    "You uploaded not your own transcript"
                )

            try:
                enrollment_year = int(student_info.get("enrollment_year"))
                current_year = datetime.now(timezone.utc).year
                study_year = max(1, current_year - enrollment_year)
            except Exception:
                study_year = user.study_year or 1

            await self.user_repo.update(
                user,
                major=student_info.get("major"),
                cgpa=student_info.get("overall_gpa"),
                total_credits_earned=student_info.get("credits_earned"),
                total_credits_enrolled=student_info.get("credits_enrolled"),
                study_year=study_year,
                is_onboarded=True,
            )

            for course_data in student_info["courses"]:
                raw_code = course_data.get("course_code", "")
                course_code, course_level = self._parse_course_identity(
                    raw_code
                )
                course_term = self._course_term(course_data)
                course_year = self._course_year(course_data)
                course_title = course_data.get("course_title", "")
                course_ects = course_data.get("ects", 3)

                course = await self.course_repo.get_or_create(
                    course_code,
                    course_level,
                    course_term,
                    course_year,
                    defaults={
                        "title": course_title,
                        "department": course_code or None,
                        "ects": course_ects,
                        "section": None,
                    },
                )

                await self.enrollment_repo.create(
                    user_id=user_id,
                    course_id=course.id,
                    term=course_term,
                    year=course_year,
                    grade=course_data.get("grade", ""),
                    grade_points=float(course_data.get("grade_points", 0) or 0),
                    status=get_enrollment_status(course_data.get("grade")),
                )

            await self._set_upload_status(upload_id, "completed")
            logger.info(
                "Transcript upload completed",
                extra={
                    "upload_id": upload_id,
                    "user_id": user_id,
                    "courses_count": len(student_info["courses"]),
                },
            )
            return upload_id
        except (FileValidationError, TranscriptParsingError):
            raise
        except Exception as exc:
            logger.exception(
                "Transcript upload failed",
                extra={
                    "upload_id": upload_id,
                    "user_id": user_id,
                    "filename": file.filename,
                },
            )
            await self._set_upload_status(
                upload_id,
                "failed",
                "Unexpected error while processing transcript",
            )
            raise TranscriptParsingError(
                "Failed to process transcript"
            ) from exc

    async def save_manual_entries(self, user_id: int, data: dict) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise FileValidationError("User not found")

        major = data.get("major")
        courses = data.get("courses", [])
        if not courses:
            raise FileValidationError("At least one course is required")

        await self.user_repo.update(
            user,
            major=major or user.major,
            is_onboarded=True,
        )

        for course_data in courses:
            raw_code = course_data.get("code", "").strip()
            course_code, course_level = self._parse_course_identity(raw_code)
            course_term = self._course_term(course_data)
            course_year = self._course_year(course_data)
            course_title = course_data.get("title", "").strip()
            if not course_code or not course_title:
                continue

            course = await self.course_repo.get_or_create(
                course_code,
                course_level,
                course_term,
                course_year,
                defaults={
                    "title": course_title,
                    "department": course_code or None,
                    "ects": int(course_data.get("ects", 3) or 3),
                    "section": None,
                },
            )

            existing = await self.enrollment_repo.get_by_user_and_course(
                user_id=user_id,
                course_id=course.id,
                term=course_term,
                year=course_year,
            )
            if existing:
                continue

            await self.enrollment_repo.create(
                user_id=user_id,
                course_id=course.id,
                term=course_term,
                year=course_year,
                grade=course_data.get("grade", ""),
                grade_points=float(course_data.get("grade_points", 0) or 0),
                status=get_enrollment_status(course_data.get("grade")),
            )

    def _parse_course_identity(self, raw_code: str) -> tuple[str, str]:
        text = (raw_code or "").strip().upper()
        match = re.search(r"([A-Z]+)\s*(\d+[A-Z]?)", text)
        if match:
            code = match.group(1).strip()
            level = match.group(2).strip()
            return code, level

        letters = re.match(r"([A-Z]+)", text)
        if letters:
            return letters.group(1).strip(), "0"
        return text, "0"

    def _course_term(self, course_data: dict) -> str:
        term = str(course_data.get("term", "")).strip()
        if not term:
            raise FileValidationError("Course term is required")
        return normalize_term(term)

    def _course_year(self, course_data: dict) -> int:
        try:
            year = int(course_data.get("year", 0) or 0)
        except (TypeError, ValueError) as exc:
            raise FileValidationError("Course year is required") from exc
        if year < 2000:
            raise FileValidationError("Course year is required")
        return year
