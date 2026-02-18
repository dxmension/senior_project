from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError, FileValidationError
from app.models.enrollment import EnrollmentStatus
from app.models.transcript import TranscriptStatus
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.transcript import TranscriptRepository
from app.repositories.user import UserRepository
from app.schemas.transcript import ParsedTranscriptData, TranscriptStatusResponse
from app.storage import LocalStorage
from app.tasks.parse_transcript import parse_transcript_task

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class TranscriptService:
    def __init__(self, session: AsyncSession, storage: LocalStorage) -> None:
        self.session = session
        self.transcript_repo = TranscriptRepository(session)
        self.course_repo = CourseRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.user_repo = UserRepository(session)
        self.storage = storage

    async def upload(self, user_id: int, file: UploadFile) -> TranscriptStatusResponse:
        if file.content_type != "application/pdf":
            raise FileValidationError("Only PDF files are accepted")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise FileValidationError("File size exceeds 10MB limit")

        key = f"transcripts/{user_id}/{file.filename}"
        file_url = await self.storage.upload(key, content)

        existing = await self.transcript_repo.get_by_user_id(user_id)
        if existing:
            transcript = await self.transcript_repo.update(
                existing,
                file_url=file_url,
                status=TranscriptStatus.PENDING,
                parsed_data=None,
                raw_text=None,
                error_message=None,
            )
        else:
            transcript = await self.transcript_repo.create(
                user_id=user_id, file_url=file_url, status=TranscriptStatus.PENDING
            )

        parse_transcript_task.delay(str(transcript.id))

        return TranscriptStatusResponse.model_validate(transcript)

    async def get_status(self, user_id: int) -> TranscriptStatusResponse:
        transcript = await self.transcript_repo.get_by_user_id(user_id)
        if not transcript:
            raise NotFoundError("Transcript")
        return TranscriptStatusResponse.model_validate(transcript)

    async def confirm(self, user_id: int, data: ParsedTranscriptData) -> None:
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User")

        if data.major:
            await self.user_repo.update(user, major=data.major)

        for record in data.courses:
            code_digits = record.code.split()[-1] if " " in record.code else record.code[-3:]
            level = int(code_digits[0]) * 100 if code_digits and code_digits[0].isdigit() else 0

            course = await self.course_repo.get_or_create(
                code=record.code,
                defaults={
                    "title": record.title,
                    "ects": record.ects,
                    "level": level,
                },
            )

            existing = await self.enrollment_repo.get_by_user_and_course(
                user_id=user_id, course_id=course.id, semester=record.semester
            )
            if not existing:
                await self.enrollment_repo.create(
                    user_id=user_id,
                    course_id=course.id,
                    semester=record.semester,
                    term=record.term,
                    grade=record.grade,
                    grade_points=record.grade_points,
                    status=EnrollmentStatus.PASSED,
                )

        transcript = await self.transcript_repo.get_by_user_id(user_id)
        if transcript:
            await self.transcript_repo.update(
                transcript,
                status=TranscriptStatus.COMPLETED,
                major=data.major,
                gpa=data.gpa,
                total_credits_earned=data.total_credits_earned,
                total_credits_enrolled=data.total_credits_enrolled,
            )

        await self.user_repo.update(user, is_onboarded=True)

    async def manual_entry(self, user_id: int, data: ParsedTranscriptData) -> None:
        transcript = await self.transcript_repo.get_by_user_id(user_id)
        if not transcript:
            await self.transcript_repo.create(
                user_id=user_id, status=TranscriptStatus.COMPLETED
            )
        await self.confirm(user_id, data)
