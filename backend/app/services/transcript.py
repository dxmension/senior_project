from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import NotFoundError, FileValidationError, TranscriptParsingError
from app.models.enrollment import EnrollmentStatus
from app.repositories.course import CourseRepository
from app.repositories.enrollment import EnrollmentRepository
from app.repositories.user import UserRepository

from app.utils.transcript import parse_transcript_from_bytes, get_enrollment_status

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class TranscriptService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.course_repo = CourseRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.user_repo = UserRepository(session)

    async def upload(self, user_id: int, file: UploadFile) -> None:
        if file.content_type != "application/pdf":
            raise FileValidationError("Only PDF files are accepted")

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise FileValidationError("File size exceeds 10MB limit")

        # TODO: celery task to process trancirpt
        # parse_transcript_task.delay(str(transcript.id))

        # parse transcript inside the http logic (bad for production, good enough for senior project ig)
        student_info = parse_transcript_from_bytes(content)

        # update student info and create enrollment entities for each transcript entry
        if student_info and student_info.get("courses"):
            
            # validate whether user uplods his/her own transcript
            student_name = student_info["student_name"].split()
            first_name, last_name = student_name[1], student_name[0]

            user = await self.user_repo.get_by_name(first_name, last_name)
            if not user or user.id != user_id:
                raise FileValidationError("You uploaded not your own transcript")

            await self.user_repo.update(
                user,
                major=student_info["major"],
                cgpa=student_info["overall_gpa"],
                total_credits_earned=student_info["credits_earned"],
                total_credits_enrolled=student_info["credits_enrolled"],
                study_year=2026 - int(
                    student_info.get("enrollment_semester").split()[-1]
                ),  # blya pizdec kostyl'
                is_onboarded=True
            )

            for c in student_info["courses"]:
                course_code = c.get("course_code", "")
                course_title = c.get("course_title", "")
                course_level = int(course_code.split()[-1][0]) * 100 if course_code and len(course_code.split()) > 1 else 100
                course_ects = c.get("ects", 3)
                
                course = await self.course_repo.get_or_create(
                    course_code,
                    defaults={
                        "title": course_title,
                        "level": course_level,
                        "ects": course_ects
                    }
                )

                # create an enrollment for a user
                await self.enrollment_repo.create(
                    user_id=user_id,
                    course_id=course.id,
                    semester=c.get("semester", ""),
                    grade=c.get("grade", ""),
                    grade_points=float(c.get("grade_points", 0)),
                    status=get_enrollment_status(c.get("grade")),
                )

            return None
        else:
            raise TranscriptParsingError(
                "Failed to parse transcript, please try again later"
            )
