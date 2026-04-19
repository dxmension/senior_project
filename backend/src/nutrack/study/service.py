import asyncio
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.assessments.models import Assessment
from nutrack.assessments.repository import AssessmentRepository
from nutrack.assessments.utils import assessment_label, mock_exam_title
from nutrack.config import settings
from nutrack.courses.models import CourseOffering
from nutrack.enrollments.models import EnrollmentStatus
from nutrack.enrollments.repository import EnrollmentRepository
from nutrack.storage import ObjectStorage, sanitize_filename, slugify
from nutrack.study.exceptions import (
    MockExamAttemptNotFoundError,
    MockExamForbiddenError,
    MockExamNotFoundError,
    MockExamQuestionNotFoundError,
    MockExamValidationError,
    StudyMaterialForbiddenError,
    StudyMaterialNotFoundError,
    StudyMaterialQueueError,
    StudyMaterialValidationError,
)
from nutrack.study.models import (
    MaterialCurationStatus,
    MaterialUploadStatus,
    MockExam,
    MockExamAttempt,
    MockExamAttemptStatus,
    MockExamQuestion,
    MockExamQuestionSource,
    MockExamQuestionLink,
    StudyMaterialLibraryEntry,
    StudyMaterialUpload,
)
from nutrack.study.repository import (
    MockExamAttemptAnswerRepository,
    MockExamAttemptRepository,
    MockExamQuestionRepository,
    MockExamRepository,
    StudyMaterialLibraryRepository,
    StudyMaterialUploadRepository,
)
from nutrack.study.utils import predicted_grade_letter, predicted_score_average

MAX_FILE_SIZE = 25 * 1024 * 1024
MAX_FILES_PER_BATCH = 10
STALE_UPLOAD_MINUTES = 15
ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}
ELIGIBLE_ASSESSMENT_TYPES = {"quiz", "midterm", "final"}


def format_course_code(code: str, level: str) -> str:
    return f"{code} {level}".strip() if level and level != "0" else code


def _attempt_completed_at(attempt: MockExamAttempt) -> datetime:
    return attempt.submitted_at or attempt.started_at


def _publish_requested(status: MaterialCurationStatus) -> bool:
    return status != MaterialCurationStatus.NOT_REQUESTED


def _admin_visible_curation_statuses(
    curation_status: MaterialCurationStatus | None,
) -> tuple[MaterialCurationStatus, ...]:
    visible_statuses = (
        MaterialCurationStatus.PENDING,
        MaterialCurationStatus.PUBLISHED,
    )
    if curation_status is None:
        return visible_statuses
    if curation_status in visible_statuses:
        return (curation_status,)
    return ()


def _upload_response(
    upload: StudyMaterialUpload,
    download_url: str | None,
):
    course = upload.course_offering.course
    return {
        "id": upload.id,
        "course_id": upload.course_id,
        "course_code": format_course_code(course.code, course.level),
        "course_title": course.title,
        "week": upload.user_week,
        "original_filename": upload.original_filename,
        "content_type": upload.content_type,
        "file_size_bytes": upload.file_size_bytes,
        "upload_status": upload.upload_status.value,
        "curation_status": upload.curation_status.value,
        "publish_requested": _publish_requested(upload.curation_status),
        "error_message": upload.error_message,
        "is_published": upload.library_entry is not None,
        "download_url": download_url,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }


def _library_response(
    entry: StudyMaterialLibraryEntry,
    download_url: str | None,
    current_user_id: int,
):
    upload = entry.upload
    course = upload.course_offering.course
    return {
        "id": entry.id,
        "upload_id": upload.id,
        "course_id": entry.course_id,
        "course_code": format_course_code(course.code, course.level),
        "course_title": course.title,
        "week": entry.curated_week,
        "title": entry.curated_title,
        "original_filename": upload.original_filename,
        "content_type": upload.content_type,
        "file_size_bytes": upload.file_size_bytes,
        "download_url": download_url,
        "is_owned_by_current_user": upload.uploader_id == current_user_id,
        "published_at": entry.updated_at,
    }


def _admin_upload_response(
    upload: StudyMaterialUpload,
    download_url: str | None,
):
    course = upload.course_offering.course
    uploader = upload.uploader
    library_entry = upload.library_entry
    return {
        "id": upload.id,
        "course_id": upload.course_id,
        "course_code": format_course_code(course.code, course.level),
        "course_title": course.title,
        "uploader_id": uploader.id,
        "uploader_name": f"{uploader.first_name} {uploader.last_name}",
        "uploader_email": uploader.email,
        "user_week": upload.user_week,
        "shared_week": library_entry.curated_week if library_entry else None,
        "shared_title": library_entry.curated_title if library_entry else None,
        "original_filename": upload.original_filename,
        "content_type": upload.content_type,
        "file_size_bytes": upload.file_size_bytes,
        "upload_status": upload.upload_status.value,
        "curation_status": upload.curation_status.value,
        "error_message": upload.error_message,
        "download_url": download_url,
        "created_at": upload.created_at,
        "updated_at": upload.updated_at,
    }


def _assessment_number_value(value: object) -> int | None:
    if isinstance(value, int) and value > 0:
        return value
    if not isinstance(value, str):
        return None
    match = re.search(r"(\d+)", value)
    if not match:
        return None
    return int(match.group(1))


def _assessment_number(exam: MockExam) -> int:
    direct = _assessment_number_value(getattr(exam, "assessment_number", None))
    if direct is not None:
        return direct
    for value in (getattr(exam, "assessment_title", None), getattr(exam, "title", None)):
        parsed = _assessment_number_value(value)
        if parsed is not None:
            return parsed
    return 1


def _offering_label(offering: CourseOffering | None) -> str | None:
    if offering is None:
        return None
    section = offering.section or "No section"
    return f"{offering.term} {offering.year} · {section}"


def _question_source_label(source: MockExamQuestionSource) -> str:
    labels = {
        MockExamQuestionSource.AI: "AI",
        MockExamQuestionSource.HISTORIC: "Historic",
        MockExamQuestionSource.RUMORED: "Rumored",
        MockExamQuestionSource.TUTOR_MADE: "Tutor made",
    }
    return labels[source]


def _attempt_response(attempt: MockExamAttempt) -> dict:
    return {
        "id": attempt.id,
        "status": attempt.status.value,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "last_active_at": attempt.last_active_at,
        "current_position": attempt.current_position,
        "answered_count": attempt.answered_count,
        "correct_count": attempt.correct_count,
        "score_pct": attempt.score_pct,
    }


def _question_response(question: MockExamQuestion) -> dict:
    offering = question.__dict__.get("historical_course_offering")
    return {
        "id": question.id,
        "course_id": question.course_id,
        "source": question.source.value,
        "source_label": _question_source_label(question.source),
        "historical_course_offering_id": question.historical_course_offering_id,
        "historical_course_offering_label": _offering_label(offering),
        "question_text": question.question_text,
        "answer_variant_1": question.answer_variant_1,
        "answer_variant_2": question.answer_variant_2,
        "answer_variant_3": question.answer_variant_3,
        "answer_variant_4": question.answer_variant_4,
        "answer_variant_5": question.answer_variant_5,
        "answer_variant_6": question.answer_variant_6,
        "correct_option_index": question.correct_option_index,
        "explanation": question.explanation,
        "created_at": question.created_at,
        "updated_at": question.updated_at,
    }


def _student_question_response(question: MockExamQuestion) -> dict:
    offering = question.__dict__.get("historical_course_offering")
    return {
        "id": question.id,
        "course_id": question.course_id,
        "source": question.source.value,
        "source_label": _question_source_label(question.source),
        "historical_course_offering_id": question.historical_course_offering_id,
        "historical_course_offering_label": _offering_label(offering),
        "question_text": question.question_text,
        "answer_variant_1": question.answer_variant_1,
        "answer_variant_2": question.answer_variant_2,
        "answer_variant_3": question.answer_variant_3,
        "answer_variant_4": question.answer_variant_4,
        "answer_variant_5": question.answer_variant_5,
        "answer_variant_6": question.answer_variant_6,
    }


def _review_question_response(question: MockExamQuestion) -> dict:
    return {
        **_student_question_response(question),
        "correct_option_index": question.correct_option_index,
        "explanation": question.explanation,
    }


def _question_link_response(link) -> dict:
    return {
        "id": link.id,
        "position": link.position,
        "points": link.points,
        "question": _question_response(link.question),
    }


def _student_question_link_response(link) -> dict:
    return {
        "id": link.id,
        "position": link.position,
        "points": link.points,
        "question": _student_question_response(link.question),
    }


class StudyService:
    def __init__(
        self,
        session: AsyncSession,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.mock_exam_repo = MockExamRepository(session)
        self.mock_exam_question_repo = MockExamQuestionRepository(session)
        self.mock_exam_attempt_repo = MockExamAttemptRepository(session)
        self.mock_exam_answer_repo = MockExamAttemptAnswerRepository(session)
        self.upload_repo = StudyMaterialUploadRepository(session)
        self.library_repo = StudyMaterialLibraryRepository(session)
        self.storage = storage or ObjectStorage()

    async def queue_uploads(
        self,
        user_id: int,
        course_id: int,
        week: int,
        request_shared_library: bool,
        files: list[UploadFile],
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        offering = await self.upload_repo.get_enrolled_course(user_id, course_id)
        if not offering:
            raise StudyMaterialForbiddenError()
        self._validate_batch(week, files)
        uploads = []
        for file in files:
            uploads.append(
                await self._create_upload(
                    user_id,
                    offering,
                    week,
                    request_shared_library,
                    file,
                )
            )
        await self.session.commit()
        try:
            self._enqueue_uploads(uploads)
        except StudyMaterialQueueError:
            await self._mark_queue_failure(uploads)
            raise
        refreshed = [await self.upload_repo.get_upload_by_id(item.id) for item in uploads]
        return await self._serialize_uploads(refreshed)

    async def list_user_uploads(
        self,
        user_id: int,
        course_id: int,
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        await self._require_course_access(user_id, course_id)
        uploads = await self.upload_repo.list_user_uploads(user_id, course_id)
        return await self._serialize_uploads(uploads)

    async def list_shared_library(
        self,
        user_id: int,
        course_id: int,
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        await self._require_course_access(user_id, course_id)
        entries = await self.library_repo.list_course_library(course_id)
        return await self._serialize_library(entries, user_id)

    async def list_admin_uploads(
        self,
        *,
        course_id: int | None = None,
        user_id: int | None = None,
        upload_status: str | None = None,
        curation_status: MaterialCurationStatus | None = None,
    ) -> list[dict]:
        await self._cleanup_stale_uploads()
        curation_statuses = _admin_visible_curation_statuses(curation_status)
        if not curation_statuses:
            return []
        uploads = await self.upload_repo.list_admin_uploads(
            course_id=course_id,
            user_id=user_id,
            upload_status=upload_status,
            curation_statuses=curation_statuses,
        )
        payload = []
        for upload in uploads:
            url = await self._download_url(upload.storage_key, upload.upload_status)
            payload.append(_admin_upload_response(upload, url))
        return payload

    async def list_mock_exams(self, user_id: int) -> list[dict]:
        enrollments = await self.enrollment_repo.list_by_user(
            user_id,
            EnrollmentStatus.IN_PROGRESS,
        )
        assessments = await self.assessment_repo.get_by_user(
            user_id,
            upcoming_only=True,
            completed=False,
        )
        items = self._eligible_assessments(assessments)
        allowed_types = self._eligible_exam_types(items)
        courses = self._current_study_courses(enrollments)
        course_ids = list(courses)
        exams = await self.mock_exam_repo.list_matching(course_ids)
        available = self._available_mock_exams(exams, allowed_types)
        stats_map = await self._student_attempt_stats(user_id, available)
        prediction_map = await self._student_prediction_map(user_id, available)
        return self._group_mock_exam_items(
            courses,
            available,
            stats_map,
            prediction_map,
        )

    async def get_mock_exam_flashcards(
        self, user_id: int, mock_exam_id: int
    ) -> list[dict]:
        exam = await self._require_student_exam_access(user_id, mock_exam_id)
        result = []
        for link in sorted(exam.question_links, key=lambda l: l.position):
            q = link.question
            correct_idx = q.correct_option_index
            correct_answer = getattr(q, f"answer_variant_{correct_idx}", "")
            answer_parts = [correct_answer]
            if q.explanation:
                answer_parts.append(q.explanation)
            result.append(
                {
                    "id": q.id,
                    "question": q.question_text,
                    "answer": " — ".join(answer_parts),
                }
            )
        return result

    async def get_mock_exam_dashboard(self, user_id: int, mock_exam_id: int) -> dict:
        exam = await self._require_student_exam_access(user_id, mock_exam_id)
        attempts = await self.mock_exam_attempt_repo.list_for_user_exam(user_id, exam.id)
        return self._dashboard_payload(exam, attempts)

    async def start_mock_exam_attempt(
        self,
        user_id: int,
        mock_exam_id: int,
    ) -> dict:
        exam = await self._require_student_exam_access(user_id, mock_exam_id)
        if not exam.question_links:
            raise MockExamValidationError("This mock exam has no questions")
        active = await self.mock_exam_attempt_repo.get_active(user_id, mock_exam_id)
        if active:
            return _attempt_response(active)
        now = datetime.now(timezone.utc)
        attempt = await self.mock_exam_attempt_repo.create(
            user_id=user_id,
            mock_exam_id=mock_exam_id,
            status=MockExamAttemptStatus.IN_PROGRESS,
            started_at=now,
            last_active_at=now,
            current_position=1,
            answered_count=0,
            correct_count=0,
            score_pct=None,
            submitted_at=None,
        )
        return _attempt_response(attempt)

    async def get_mock_exam_attempt(
        self,
        user_id: int,
        attempt_id: int,
    ) -> dict:
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        return self._attempt_session_payload(attempt)

    async def get_mock_exam_attempt_review(
        self,
        user_id: int,
        attempt_id: int,
    ) -> dict:
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        if attempt.status != MockExamAttemptStatus.COMPLETED:
            raise MockExamValidationError("Only completed attempts can be reviewed")
        return self._attempt_review_payload(attempt)

    async def save_mock_exam_answer(
        self,
        user_id: int,
        attempt_id: int,
        link_id: int,
        selected_option_index: int | None,
    ) -> dict:
        attempt = await self._require_active_attempt(user_id, attempt_id)
        exam = await self.mock_exam_repo.get_by_id_with_links(attempt.mock_exam_id)
        link = self._find_question_link(exam, link_id)
        answer = await self.mock_exam_answer_repo.get_by_attempt_and_link(attempt.id, link_id)
        now = datetime.now(timezone.utc)
        is_correct = None
        if selected_option_index is not None:
            self._validate_selected_option(link.question, selected_option_index)
            is_correct = selected_option_index == link.question.correct_option_index
        if answer:
            await self.mock_exam_answer_repo.update(
                answer,
                selected_option_index=selected_option_index,
                is_correct=is_correct,
                answered_at=now if selected_option_index is not None else None,
            )
        else:
            answer = await self.mock_exam_answer_repo.create(
                attempt_id=attempt.id,
                mock_exam_question_link_id=link_id,
                selected_option_index=selected_option_index,
                is_correct=is_correct,
                answered_at=now if selected_option_index is not None else None,
            )
        await self._refresh_attempt_progress(attempt, exam)
        return self._answer_payload(answer)

    async def submit_mock_exam_attempt(
        self,
        user_id: int,
        attempt_id: int,
    ) -> dict:
        attempt = await self._require_active_attempt(user_id, attempt_id)
        exam = await self.mock_exam_repo.get_by_id_with_links(attempt.mock_exam_id)
        await self._refresh_attempt_progress(attempt, exam)
        total = max(len(exam.question_links), 1)
        now = datetime.now(timezone.utc)
        score_pct = round(attempt.correct_count / total * 100, 1)
        await self.mock_exam_attempt_repo.update(
            attempt,
            status=MockExamAttemptStatus.COMPLETED,
            submitted_at=now,
            last_active_at=now,
            score_pct=score_pct,
        )
        return _attempt_response(attempt)

    async def list_admin_mock_exams(self, course_id: int) -> list[dict]:
        exams = await self.mock_exam_repo.list_by_course(course_id)
        stats = await self.mock_exam_attempt_repo.get_attempt_stats([exam.id for exam in exams])
        return [self._admin_exam_payload(exam, stats.get(exam.id, {})) for exam in exams]

    async def get_admin_mock_exam_detail(self, mock_exam_id: int) -> dict:
        exam = await self._load_mock_exam(mock_exam_id)
        stats = await self.mock_exam_attempt_repo.get_attempt_stats([mock_exam_id])
        return {
            "exam": self._admin_exam_payload(exam, stats.get(mock_exam_id, {})),
            "questions": self._question_links_payload(exam),
        }

    async def create_mock_exam(self, admin_id: int, payload) -> dict:
        questions = await self._validated_questions(payload.course_id, payload.questions)
        number = payload.assessment_number
        label = assessment_label(payload.assessment_type, number)
        latest = await self.mock_exam_repo.get_latest_version(
            payload.course_id,
            payload.assessment_type.value,
            number,
        )
        version = 1 if not latest else latest.version + 1
        title = mock_exam_title(payload.assessment_type, number, version)
        if payload.is_active:
            await self.mock_exam_repo.deactivate_family(
                payload.course_id,
                payload.assessment_type.value,
                number,
            )
        exam = await self.mock_exam_repo.create(
            course_id=payload.course_id,
            assessment_type=payload.assessment_type,
            assessment_number=number,
            assessment_title=label,
            assessment_title_slug=slugify(label).strip("-"),
            title=title,
            version=version,
            question_count=len(payload.questions),
            time_limit_minutes=payload.time_limit_minutes,
            instructions=payload.instructions,
            is_active=payload.is_active,
            created_by_admin_id=admin_id,
        )
        await self._create_question_links(exam.id, payload.questions)
        return await self.get_admin_mock_exam_detail(exam.id)

    async def update_mock_exam(self, admin_id: int, mock_exam_id: int, payload) -> dict:
        current = await self._load_mock_exam(mock_exam_id)
        question_items = payload.questions or self._clone_question_links(current)
        request = type("MockExamUpdatePayload", (), {})()
        request.course_id = current.course_id
        request.assessment_type = current.assessment_type
        request.assessment_number = (
            payload.assessment_number
            if payload.assessment_number is not None
            else _assessment_number(current)
        )
        request.time_limit_minutes = payload.time_limit_minutes
        if request.time_limit_minutes is None:
            request.time_limit_minutes = current.time_limit_minutes
        request.instructions = payload.instructions
        if payload.instructions is None:
            request.instructions = current.instructions
        request.is_active = current.is_active if payload.is_active is None else payload.is_active
        request.questions = question_items
        return await self.create_mock_exam(admin_id, request)

    async def deactivate_mock_exam(self, mock_exam_id: int) -> dict:
        exam = await self._load_mock_exam(mock_exam_id)
        await self.mock_exam_repo.update(exam, is_active=False)
        return {"deactivated": True}

    async def delete_mock_exam(self, mock_exam_id: int) -> dict:
        exam = await self._load_mock_exam(mock_exam_id)
        attempts = await self.mock_exam_repo.count_attempts(mock_exam_id)
        if attempts > 0:
            raise MockExamValidationError("Mock exams with attempts cannot be deleted")
        await self.mock_exam_repo.delete(exam)
        return {"deleted": True}

    async def list_admin_mock_exam_questions(self, course_id: int) -> list[dict]:
        questions = await self.mock_exam_question_repo.list_by_course(course_id)
        usage_map = await self.mock_exam_question_repo.usage_counts([q.id for q in questions])
        payload = []
        for question in questions:
            payload.append(
                {
                    **_question_response(question),
                    "usage_count": usage_map.get(question.id, 0),
                }
            )
        return payload

    async def create_mock_exam_question(self, admin_id: int, payload) -> dict:
        self._validate_question_payload(payload)
        await self._validate_question_source(payload.course_id, payload)
        question = await self.mock_exam_question_repo.create(
            course_id=payload.course_id,
            source=payload.source,
            historical_course_offering_id=payload.historical_course_offering_id,
            question_text=payload.question_text.strip(),
            answer_variant_1=payload.answer_variant_1.strip(),
            answer_variant_2=payload.answer_variant_2.strip(),
            answer_variant_3=self._clean_optional_text(payload.answer_variant_3),
            answer_variant_4=self._clean_optional_text(payload.answer_variant_4),
            answer_variant_5=self._clean_optional_text(payload.answer_variant_5),
            answer_variant_6=self._clean_optional_text(payload.answer_variant_6),
            correct_option_index=payload.correct_option_index,
            explanation=self._clean_optional_text(payload.explanation),
            created_by_admin_id=admin_id,
        )
        return {**_question_response(question), "usage_count": 0}

    async def update_mock_exam_question(
        self,
        question_id: int,
        payload,
    ) -> dict:
        question = await self.mock_exam_question_repo.get_by_id(question_id)
        if not question:
            raise MockExamQuestionNotFoundError()
        if await self.mock_exam_question_repo.is_linked(question_id):
            raise MockExamValidationError("Linked questions cannot be edited in place")
        data = self._merged_question_payload(question, payload)
        self._validate_question_payload(data)
        await self._validate_question_source(question.course_id, data)
        await self.mock_exam_question_repo.update(
            question,
            source=data.source,
            historical_course_offering_id=data.historical_course_offering_id,
            question_text=data.question_text,
            answer_variant_1=data.answer_variant_1,
            answer_variant_2=data.answer_variant_2,
            answer_variant_3=data.answer_variant_3,
            answer_variant_4=data.answer_variant_4,
            answer_variant_5=data.answer_variant_5,
            answer_variant_6=data.answer_variant_6,
            correct_option_index=data.correct_option_index,
            explanation=data.explanation,
        )
        return {**_question_response(question), "usage_count": 0}

    async def delete_mock_exam_question(self, question_id: int) -> dict:
        question = await self.mock_exam_question_repo.get_by_id(question_id)
        if not question:
            raise MockExamQuestionNotFoundError()
        if await self.mock_exam_question_repo.is_linked(question_id):
            raise MockExamValidationError("Linked questions cannot be deleted")
        await self.mock_exam_question_repo.delete(question)
        return {"deleted": True}

    async def publish_upload(
        self,
        admin_id: int,
        upload_id: int,
        title: str,
        week: int,
    ) -> dict:
        await self._cleanup_stale_uploads()
        self._validate_week(week)
        if not title.strip():
            raise StudyMaterialValidationError("Title is required")
        upload = await self._load_upload(upload_id)
        if upload.upload_status != MaterialUploadStatus.COMPLETED:
            raise StudyMaterialValidationError("Only completed uploads can be published")
        if not _publish_requested(upload.curation_status):
            raise StudyMaterialValidationError(
                "This upload was not submitted for shared library curation"
            )
        library_entry = await self.library_repo.get_by_upload_id(upload.id)
        if library_entry:
            await self.library_repo.update(
                library_entry,
                curated_title=title.strip(),
                curated_week=week,
                curated_by_admin_id=admin_id,
            )
        else:
            library_entry = await self.library_repo.create(
                upload_id=upload.id,
                course_id=upload.course_id,
                curated_title=title.strip(),
                curated_week=week,
                curated_by_admin_id=admin_id,
            )
        await self.upload_repo.update(
            upload,
            curation_status=MaterialCurationStatus.PUBLISHED,
        )
        await self.session.commit()
        loaded = await self.library_repo.get_by_upload_id(upload.id)
        return _library_response(
            loaded,
            await self.storage.generate_download_url(upload.storage_key),
            upload.uploader_id,
        )

    async def reject_upload(self, upload_id: int) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_upload(upload_id)
        if upload.library_entry is not None:
            raise StudyMaterialValidationError("Published uploads cannot be rejected")
        if not _publish_requested(upload.curation_status):
            raise StudyMaterialValidationError("Private uploads cannot be rejected")
        await self.upload_repo.update(
            upload,
            curation_status=MaterialCurationStatus.REJECTED,
        )
        await self.session.commit()
        return {"rejected": True}

    async def cancel_user_publish(
        self,
        user_id: int,
        course_id: int,
        upload_id: int,
    ) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_user_upload(user_id, course_id, upload_id)
        return await self._make_upload_private(upload)

    async def unpublish_upload(self, upload_id: int) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_upload(upload_id)
        return await self._make_upload_private(upload)

    async def delete_user_upload(
        self,
        user_id: int,
        course_id: int,
        upload_id: int,
    ) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_user_upload(user_id, course_id, upload_id)
        return await self._delete_upload(upload)

    async def delete_upload(self, upload_id: int) -> dict:
        await self._cleanup_stale_uploads()
        upload = await self._load_upload(upload_id)
        return await self._delete_upload(upload)

    async def mark_upload_failed(
        self,
        upload_id: int,
        message: str,
    ) -> None:
        upload = await self.upload_repo.get_upload_by_id(upload_id)
        if not upload:
            return
        staged_path = upload.staged_path
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.FAILED,
            staged_path=None,
            error_message=message[:500],
        )
        await self.session.commit()
        await self._remove_staged_file(staged_path)

    async def process_upload(self, upload_id: int) -> None:
        upload = await self._load_upload(upload_id)
        if upload.upload_status == MaterialUploadStatus.COMPLETED:
            return
        if not upload.staged_path:
            raise StudyMaterialValidationError("Staged upload file is missing")
        staged_path = upload.staged_path
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.UPLOADING,
            error_message=None,
        )
        await self.session.commit()
        await self.storage.ensure_bucket()
        await self.storage.upload_file(
            upload.staged_path,
            upload.storage_key,
            upload.content_type,
        )
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.COMPLETED,
            staged_path=None,
            error_message=None,
        )
        await self.session.commit()
        await self._remove_staged_file(staged_path)

    async def _create_upload(
        self,
        user_id: int,
        offering,
        week: int,
        request_shared_library: bool,
        file: UploadFile,
    ) -> StudyMaterialUpload:
        filename = self._validate_file(file)
        payload = await file.read()
        if not payload:
            raise StudyMaterialValidationError("Uploaded file is empty")
        if len(payload) > MAX_FILE_SIZE:
            raise StudyMaterialValidationError("File size exceeds 25MB")
        storage_key = self._storage_key(offering.course.title, week, filename)
        staged_path = await self._stage_file(filename, payload)
        return await self.upload_repo.create(
            course_id=offering.id,
            uploader_id=user_id,
            user_week=week,
            original_filename=filename,
            staged_path=staged_path,
            storage_key=storage_key,
            content_type=self._content_type(file, filename),
            file_size_bytes=len(payload),
            upload_status=MaterialUploadStatus.QUEUED,
            curation_status=self._curation_status(request_shared_library),
            error_message=None,
        )

    async def _require_course_access(
        self,
        user_id: int,
        course_id: int,
    ) -> None:
        if await self.upload_repo.get_enrolled_course(user_id, course_id):
            return
        raise StudyMaterialForbiddenError()

    async def _load_upload(self, upload_id: int) -> StudyMaterialUpload:
        upload = await self.upload_repo.get_upload_by_id(upload_id)
        if upload:
            return upload
        raise StudyMaterialNotFoundError()

    async def _load_user_upload(
        self,
        user_id: int,
        course_id: int,
        upload_id: int,
    ) -> StudyMaterialUpload:
        await self._require_course_access(user_id, course_id)
        upload = await self._load_upload(upload_id)
        if upload.course_id == course_id and upload.uploader_id == user_id:
            return upload
        raise StudyMaterialNotFoundError()

    async def _serialize_uploads(
        self,
        uploads: list[StudyMaterialUpload | None],
    ) -> list[dict]:
        payload = []
        for upload in uploads:
            if not upload:
                continue
            url = await self._download_url(upload.storage_key, upload.upload_status)
            payload.append(_upload_response(upload, url))
        return payload

    async def _serialize_library(
        self,
        entries: list[StudyMaterialLibraryEntry],
        user_id: int,
    ) -> list[dict]:
        payload = []
        for entry in entries:
            url = await self.storage.generate_download_url(entry.upload.storage_key)
            payload.append(_library_response(entry, url, user_id))
        return payload

    async def _download_url(
        self,
        storage_key: str,
        upload_status: MaterialUploadStatus,
    ) -> str | None:
        if upload_status != MaterialUploadStatus.COMPLETED:
            return None
        return await self.storage.generate_download_url(storage_key)

    def _enqueue_uploads(self, uploads: list[StudyMaterialUpload]) -> None:
        from nutrack.tasks.materials import upload_course_material_task

        try:
            for upload in uploads:
                upload_course_material_task.delay(upload.id)
        except Exception as exc:  # pragma: no cover - broker/network failure
            raise StudyMaterialQueueError() from exc

    def _validate_batch(self, week: int, files: list[UploadFile]) -> None:
        self._validate_week(week)
        if not files:
            raise StudyMaterialValidationError("Select at least one file")
        if len(files) > MAX_FILES_PER_BATCH:
            raise StudyMaterialValidationError("You can upload up to 10 files at once")

    def _validate_week(self, week: int) -> None:
        if 1 <= week <= 15:
            return
        raise StudyMaterialValidationError("Week must be between 1 and 15")

    def _validate_file(self, file: UploadFile) -> str:
        filename = (file.filename or "").strip()
        suffix = Path(filename).suffix.lower()
        if filename and suffix in ALLOWED_EXTENSIONS:
            return filename
        raise StudyMaterialValidationError("Unsupported file type")

    def _content_type(self, file: UploadFile, filename: str) -> str:
        return file.content_type or ALLOWED_EXTENSIONS[Path(filename).suffix.lower()]

    def _storage_key(self, course_title: str, week: int, filename: str) -> str:
        safe_name = sanitize_filename(filename)
        return f"{slugify(course_title)}/week_{week}/{uuid4()}__{safe_name}"

    async def _stage_file(self, filename: str, payload: bytes) -> str:
        directory = Path(settings.MATERIAL_UPLOAD_STAGING_DIR)
        await asyncio.to_thread(directory.mkdir, parents=True, exist_ok=True)
        path = directory / f"{uuid4()}__{sanitize_filename(filename)}"
        await asyncio.to_thread(path.write_bytes, payload)
        return str(path)

    async def _remove_staged_file(self, staged_path: str | None) -> None:
        if not staged_path:
            return
        path = Path(staged_path)
        if not path.exists():
            return
        await asyncio.to_thread(path.unlink)

    async def _delete_storage_file(self, storage_key: str | None) -> None:
        if not storage_key:
            return
        try:
            await self.storage.delete_file(storage_key)
        except Exception:
            return

    async def _mark_queue_failure(
        self,
        uploads: list[StudyMaterialUpload],
    ) -> None:
        for upload in uploads:
            staged_path = upload.staged_path
            await self.upload_repo.update(
                upload,
                upload_status=MaterialUploadStatus.FAILED,
                staged_path=None,
                error_message="Failed to queue material upload",
            )
            await self._remove_staged_file(staged_path)
        await self.session.commit()

    def _curation_status(
        self,
        request_shared_library: bool,
    ) -> MaterialCurationStatus:
        if request_shared_library:
            return MaterialCurationStatus.PENDING
        return MaterialCurationStatus.NOT_REQUESTED

    async def _make_upload_private(
        self,
        upload: StudyMaterialUpload,
    ) -> dict:
        await self._delete_library_entry(upload)
        await self.upload_repo.update(
            upload,
            curation_status=MaterialCurationStatus.NOT_REQUESTED,
        )
        await self.session.commit()
        loaded = await self.upload_repo.get_upload_by_id(upload.id)
        return _upload_response(
            loaded,
            await self._download_url(loaded.storage_key, loaded.upload_status),
        )

    async def _delete_upload(
        self,
        upload: StudyMaterialUpload,
    ) -> dict:
        staged_path = upload.staged_path
        storage_key = upload.storage_key
        await self._delete_library_entry(upload)
        await self.upload_repo.delete(upload)
        await self.session.commit()
        await self._remove_staged_file(staged_path)
        await self._delete_storage_file(storage_key)
        return {"deleted": True}

    async def _delete_library_entry(
        self,
        upload: StudyMaterialUpload,
    ) -> None:
        if upload.library_entry is None:
            return
        await self.library_repo.delete(upload.library_entry)

    def _eligible_assessments(self, assessments: list[Assessment]) -> list[Assessment]:
        return [
            item
            for item in assessments
            if item.assessment_type.value in ELIGIBLE_ASSESSMENT_TYPES
        ]

    def _eligible_exam_types(
        self,
        assessments: list[Assessment],
    ) -> dict[int, set[str]]:
        allowed: dict[int, set[str]] = {}
        for assessment in assessments:
            course_id = assessment.course_offering.course.id
            types = allowed.setdefault(course_id, set())
            types.add(assessment.assessment_type.value)
        return allowed

    def _available_mock_exams(
        self,
        exams: list[MockExam],
        allowed_types: dict[int, set[str]],
    ) -> list[MockExam]:
        available = [
            exam
            for exam in exams
            if exam.assessment_type.value in allowed_types.get(exam.course_id, set())
        ]
        return sorted(
            available,
            key=lambda exam: (
                exam.course_id,
                -exam.created_at.timestamp(),
                exam.assessment_type.value,
                _assessment_number(exam),
            ),
        )

    async def _student_attempt_stats(
        self,
        user_id: int,
        exams: list[MockExam],
    ) -> dict[int, dict[str, float | int | bool | None]]:
        exam_ids = [exam.id for exam in exams]
        return await self.mock_exam_attempt_repo.get_attempt_stats(exam_ids, user_id)

    async def _student_prediction_map(
        self,
        user_id: int,
        exams: list[MockExam],
    ) -> dict[str, dict]:
        exam_ids = [exam.id for exam in exams]
        attempts = await self.mock_exam_attempt_repo.list_for_user_exams(user_id, exam_ids)
        return self._prediction_map(exams, attempts)

    def _prediction_map(
        self,
        exams: list[MockExam],
        attempts: list[MockExamAttempt],
    ) -> dict[str, dict]:
        exam_map = {exam.id: exam for exam in exams}
        course_scores: dict[int, list[tuple[datetime, float]]] = {}
        type_scores: dict[tuple[int, str], list[tuple[datetime, float]]] = {}
        for attempt in attempts:
            if attempt.score_pct is None:
                continue
            exam = exam_map.get(attempt.mock_exam_id)
            if not exam:
                continue
            item = (_attempt_completed_at(attempt), float(attempt.score_pct))
            course_scores.setdefault(exam.course_id, []).append(item)
            key = (exam.course_id, exam.assessment_type.value)
            type_scores.setdefault(key, []).append(item)
        return {
            "course": self._recent_prediction_scores(course_scores),
            "assessment": self._recent_prediction_scores(type_scores),
        }

    def _recent_prediction_scores(
        self,
        scores_map: dict,
    ) -> dict:
        predictions = {}
        for key, values in scores_map.items():
            ordered = sorted(values, key=lambda item: item[0], reverse=True)
            latest_scores = [score for _, score in ordered[:3]]
            predictions[key] = predicted_score_average(latest_scores)
        return predictions

    def _group_mock_exam_items(
        self,
        courses: dict[int, dict[str, object]],
        exams: list[MockExam],
        stats_map: dict[int, dict[str, float | int | bool | None]],
        prediction_map: dict[str, dict],
    ) -> list[dict]:
        groups = {
            course_id: {
                "course_id": course_id,
                "course_code": data["course_code"],
                "course_title": data["course_title"],
                "predicted_score_pct": prediction_map["course"].get(course_id),
                "predicted_grade_letter": predicted_grade_letter(
                    prediction_map["course"].get(course_id)
                ),
                "assessment_predictions": [],
                "exams": [],
            }
            for course_id, data in courses.items()
        }
        seen_predictions: dict[int, set[str]] = {
            course_id: set() for course_id in courses
        }
        for exam in exams:
            stats = stats_map.get(exam.id, {})
            group = groups[exam.course_id]
            assessment_type = exam.assessment_type.value
            if assessment_type not in seen_predictions[exam.course_id]:
                seen_predictions[exam.course_id].add(assessment_type)
                group["assessment_predictions"].append(
                    {
                        "assessment_type": assessment_type,
                        "predicted_score_pct": prediction_map["assessment"].get(
                            (exam.course_id, assessment_type)
                        ),
                        "predicted_grade_letter": predicted_grade_letter(
                            prediction_map["assessment"].get(
                                (exam.course_id, assessment_type)
                            )
                        ),
                    }
                )
            group["exams"].append(
                {
                    "id": exam.id,
                    "assessment_number": _assessment_number(exam),
                    "title": exam.title,
                    "assessment_type": exam.assessment_type.value,
                    "version": exam.version,
                    "question_count": exam.question_count,
                    "time_limit_minutes": exam.time_limit_minutes,
                    "created_at": exam.created_at,
                    "sources": self._exam_sources_payload(exam),
                    "best_score_pct": stats.get("best_score_pct"),
                    "average_score_pct": stats.get("average_score_pct"),
                    "latest_score_pct": stats.get("latest_score_pct"),
                    "predicted_score_pct": stats.get("predicted_score_pct"),
                    "predicted_grade_letter": predicted_grade_letter(
                        stats.get("predicted_score_pct")
                    ),
                    "attempts_count": stats.get("attempts_count", 0),
                    "completed_attempts": stats.get("completed_attempts", 0),
                    "has_active_attempt": bool(stats.get("has_active_attempt")),
                }
            )
        return list(groups.values())

    def _current_study_courses(self, enrollments: list) -> dict[int, dict[str, object]]:
        courses = {}
        ordered = sorted(
            enrollments,
            key=lambda item: (
                item.course_offering.course.code,
                item.course_offering.course.level,
            ),
        )
        for enrollment in ordered:
            course = enrollment.course_offering.course
            courses.setdefault(
                course.id,
                {
                    "course_code": format_course_code(course.code, course.level),
                    "course_title": course.title,
                },
            )
        return courses

    async def _require_student_exam_access(
        self,
        user_id: int,
        mock_exam_id: int,
    ) -> MockExam:
        exam = await self._load_mock_exam(mock_exam_id)
        assessments = await self.assessment_repo.get_by_user(user_id)
        for assessment in assessments:
            if assessment.course_offering.course.id != exam.course_id:
                continue
            if assessment.assessment_type.value == exam.assessment_type.value:
                return exam
        raise MockExamForbiddenError()

    async def _load_mock_exam(self, mock_exam_id: int) -> MockExam:
        exam = await self.mock_exam_repo.get_by_id_with_links(mock_exam_id)
        if exam:
            return exam
        raise MockExamNotFoundError()

    def _dashboard_payload(
        self,
        exam: MockExam,
        attempts: list[MockExamAttempt],
    ) -> dict:
        course = exam.course
        completed = [item for item in attempts if item.score_pct is not None]
        scores = [float(item.score_pct) for item in completed]
        latest_scores = [float(item.score_pct) for item in completed[:3]]
        best = max(scores) if scores else None
        average = predicted_score_average(scores)
        latest = scores[0] if scores else None
        predicted = predicted_score_average(latest_scores)
        improvement = round(scores[0] - scores[-1], 1) if len(scores) > 1 else None
        active = next((item for item in attempts if item.status == MockExamAttemptStatus.IN_PROGRESS), None)
        return {
            "id": exam.id,
            "course_id": exam.course_id,
            "course_code": format_course_code(course.code, course.level),
            "course_title": course.title,
            "assessment_type": exam.assessment_type.value,
            "assessment_number": _assessment_number(exam),
            "title": exam.title,
            "version": exam.version,
            "question_count": exam.question_count,
            "time_limit_minutes": exam.time_limit_minutes,
            "instructions": exam.instructions,
            "created_at": exam.created_at,
            "sources": self._exam_sources_payload(exam),
            "attempts_count": len(completed),
            "best_score_pct": best,
            "average_score_pct": average,
            "latest_score_pct": latest,
            "predicted_score_pct": predicted,
            "predicted_grade_letter": predicted_grade_letter(predicted),
            "improvement_pct": improvement,
            "active_attempt": _attempt_response(active) if active else None,
            "attempts": [self._attempt_summary(item) for item in attempts],
            "trend": self._trend_points(completed),
        }

    def _attempt_session_payload(self, attempt: MockExamAttempt) -> dict:
        exam = attempt.mock_exam
        answers = [self._answer_payload(answer) for answer in attempt.answers]
        return {
            **_attempt_response(attempt),
            **self._attempt_exam_payload(exam),
            "questions": self._student_question_links_payload(exam),
            "answers": answers,
        }

    def _attempt_review_payload(self, attempt: MockExamAttempt) -> dict:
        exam = attempt.mock_exam
        answers = {item.mock_exam_question_link_id: item for item in attempt.answers}
        questions = self._review_questions_payload(exam, answers)
        return {
            **_attempt_response(attempt),
            **self._attempt_exam_payload(exam),
            "review_questions": questions,
        }

    def _attempt_exam_payload(self, exam: MockExam) -> dict:
        course = exam.course
        return {
            "mock_exam_id": exam.id,
            "course_id": exam.course_id,
            "course_code": format_course_code(course.code, course.level),
            "course_title": course.title,
            "assessment_type": exam.assessment_type.value,
            "assessment_number": _assessment_number(exam),
            "title": exam.title,
            "question_count": exam.question_count,
            "time_limit_minutes": exam.time_limit_minutes,
            "instructions": exam.instructions,
        }

    def _exam_sources_payload(self, exam: MockExam) -> list[dict]:
        seen = set()
        sources = []
        for link in sorted(exam.question_links, key=lambda item: item.position):
            source = link.question.source
            if source in seen:
                continue
            seen.add(source)
            sources.append(
                {
                    "source": source.value,
                    "label": _question_source_label(source),
                }
            )
        return sources

    def _attempt_summary(self, attempt: MockExamAttempt) -> dict:
        return {
            "id": attempt.id,
            "status": attempt.status.value,
            "score_pct": attempt.score_pct,
            "started_at": attempt.started_at,
            "submitted_at": attempt.submitted_at,
        }

    def _trend_points(self, attempts: list[MockExamAttempt]) -> list[dict]:
        best = 0.0
        ordered = sorted(
            [item for item in attempts if item.submitted_at],
            key=lambda item: item.submitted_at,
        )
        points = []
        for attempt in ordered:
            best = max(best, float(attempt.score_pct or 0.0))
            points.append(
                {
                    "date_label": attempt.submitted_at.strftime("%b %d"),
                    "best_score_pct": round(best, 1),
                }
            )
        return points

    def _question_links_payload(self, exam: MockExam) -> list[dict]:
        links = sorted(exam.question_links, key=lambda item: item.position)
        return [_question_link_response(link) for link in links]

    def _student_question_links_payload(self, exam: MockExam) -> list[dict]:
        links = sorted(exam.question_links, key=lambda item: item.position)
        return [_student_question_link_response(link) for link in links]

    def _review_questions_payload(
        self,
        exam: MockExam,
        answers: dict[int, object],
    ) -> list[dict]:
        items = []
        links = sorted(exam.question_links, key=lambda item: item.position)
        for link in links:
            answer = answers.get(link.id)
            items.append(
                {
                    "id": link.id,
                    "position": link.position,
                    "points": link.points,
                    "selected_option_index": (
                        answer.selected_option_index if answer else None
                    ),
                    "is_correct": answer.is_correct if answer else None,
                    "question": _review_question_response(link.question),
                }
            )
        return items

    def _answer_payload(self, answer) -> dict:
        return {
            "id": answer.id,
            "mock_exam_question_link_id": answer.mock_exam_question_link_id,
            "selected_option_index": answer.selected_option_index,
            "is_correct": answer.is_correct,
            "answered_at": answer.answered_at,
        }

    async def _require_active_attempt(
        self,
        user_id: int,
        attempt_id: int,
    ) -> MockExamAttempt:
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        if attempt.status != MockExamAttemptStatus.IN_PROGRESS:
            raise MockExamValidationError("Only active attempts can be changed")
        return attempt

    def _find_question_link(self, exam: MockExam, link_id: int):
        for link in exam.question_links:
            if link.id == link_id:
                return link
        raise MockExamQuestionNotFoundError()

    async def _refresh_attempt_progress(
        self,
        attempt: MockExamAttempt,
        exam: MockExam,
    ) -> None:
        refreshed = await self.mock_exam_attempt_repo.get_by_id(attempt.id)
        answered = [item for item in refreshed.answers if item.selected_option_index is not None]
        correct = [item for item in answered if item.is_correct]
        current = refreshed.current_position
        if answered:
            current = min(max(item.question_link.position for item in answered) + 1, len(exam.question_links))
        await self.mock_exam_attempt_repo.update(
            attempt,
            answered_count=len(answered),
            correct_count=len(correct),
            current_position=max(current, 1),
            last_active_at=datetime.now(timezone.utc),
        )

    async def _validated_questions(self, course_id: int, questions: list) -> dict[int, MockExamQuestion]:
        payload: dict[int, MockExamQuestion] = {}
        for item in questions:
            question = await self.mock_exam_question_repo.get_by_id(item.question_id)
            if not question:
                raise MockExamQuestionNotFoundError()
            if question.course_id != course_id:
                raise MockExamValidationError("Question does not belong to the selected course")
            payload[item.question_id] = question
        return payload

    async def _create_question_links(
        self,
        mock_exam_id: int,
        items: list,
    ) -> None:
        for item in items:
            self.session.add(
                MockExamQuestionLink(
                    mock_exam_id=mock_exam_id,
                    question_id=item.question_id,
                    position=item.position,
                    points=item.points,
                )
            )
        await self.session.flush()

    async def _validate_offering(self, course_id: int, course_offering_id: int) -> None:
        offering = await self.session.get(CourseOffering, course_offering_id)
        if not offering or offering.course_id != course_id:
            raise MockExamValidationError("Course offering not found")

    async def _validate_question_source(self, course_id: int, payload) -> None:
        if payload.source != MockExamQuestionSource.HISTORIC:
            if payload.historical_course_offering_id is None:
                return
            raise MockExamValidationError(
                "Only historic questions can reference a course offering"
            )
        if payload.historical_course_offering_id is None:
            return
        await self._validate_offering(course_id, payload.historical_course_offering_id)

    def _validate_question_payload(self, payload) -> None:
        answers = [
            self._clean_optional_text(payload.answer_variant_1),
            self._clean_optional_text(payload.answer_variant_2),
            payload.answer_variant_3,
            payload.answer_variant_4,
            payload.answer_variant_5,
            payload.answer_variant_6,
        ]
        cleaned = [self._clean_optional_text(item) for item in answers]
        count = len([item for item in cleaned if item is not None])
        if count < 2:
            raise MockExamValidationError("Each question needs at least two answers")
        if cleaned[payload.correct_option_index - 1] is None:
            raise MockExamValidationError("Correct option must point to a non-empty answer")

    def _clean_optional_text(self, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None

    def _validate_selected_option(
        self,
        question: MockExamQuestion,
        selected_option_index: int,
    ) -> None:
        selected = getattr(question, f"answer_variant_{selected_option_index}")
        if selected is None:
            raise MockExamValidationError("Selected answer does not exist")

    def _merged_question_payload(self, question: MockExamQuestion, payload):
        data = type("QuestionPayload", (), {})()
        data.source = payload.source or question.source
        historical = payload.historical_course_offering_id
        if historical is None and payload.source == MockExamQuestionSource.HISTORIC:
            historical = question.historical_course_offering_id
        data.historical_course_offering_id = (
            historical
            if payload.historical_course_offering_id is not None or payload.source is not None
            else question.historical_course_offering_id
        )
        data.question_text = payload.question_text or question.question_text
        data.answer_variant_1 = payload.answer_variant_1 or question.answer_variant_1
        data.answer_variant_2 = payload.answer_variant_2 or question.answer_variant_2
        data.answer_variant_3 = payload.answer_variant_3 if payload.answer_variant_3 is not None else question.answer_variant_3
        data.answer_variant_4 = payload.answer_variant_4 if payload.answer_variant_4 is not None else question.answer_variant_4
        data.answer_variant_5 = payload.answer_variant_5 if payload.answer_variant_5 is not None else question.answer_variant_5
        data.answer_variant_6 = payload.answer_variant_6 if payload.answer_variant_6 is not None else question.answer_variant_6
        data.correct_option_index = payload.correct_option_index or question.correct_option_index
        data.explanation = payload.explanation if payload.explanation is not None else question.explanation
        return data

    def _clone_question_links(self, exam: MockExam) -> list:
        items = []
        for link in exam.question_links:
            clone = type("QuestionLinkPayload", (), {})()
            clone.question_id = link.question_id
            clone.position = link.position
            clone.points = link.points
            items.append(clone)
        return items

    def _admin_exam_payload(
        self,
        exam: MockExam,
        stats: dict[str, float | int | bool | None],
    ) -> dict:
        course = exam.course
        return {
            "id": exam.id,
            "course_id": exam.course_id,
            "course_code": format_course_code(course.code, course.level),
            "course_title": course.title,
            "assessment_type": exam.assessment_type.value,
            "assessment_number": _assessment_number(exam),
            "title": exam.title,
            "version": exam.version,
            "is_active": exam.is_active,
            "question_count": exam.question_count,
            "time_limit_minutes": exam.time_limit_minutes,
            "instructions": exam.instructions,
            "total_attempts": stats.get("attempts_count", 0),
            "completed_attempts": stats.get("completed_attempts", 0),
            "average_score_pct": stats.get("average_score_pct"),
            "best_score_pct": stats.get("best_score_pct"),
            "active_attempts": stats.get("active_attempts", 0),
            "created_at": exam.created_at,
            "updated_at": exam.updated_at,
        }

    async def _cleanup_stale_uploads(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=STALE_UPLOAD_MINUTES)
        statuses = (
            MaterialUploadStatus.QUEUED,
            MaterialUploadStatus.UPLOADING,
        )
        uploads = await self.upload_repo.list_stale_uploads(cutoff, statuses)
        if not uploads:
            return
        for upload in uploads:
            await self._fail_stale_upload(upload)
        await self.session.commit()

    async def _fail_stale_upload(
        self,
        upload: StudyMaterialUpload,
    ) -> None:
        staged_path = upload.staged_path
        await self.upload_repo.update(
            upload,
            upload_status=MaterialUploadStatus.FAILED,
            staged_path=None,
            error_message="Upload timed out before completion",
        )
        await self._remove_staged_file(staged_path)
        await self._delete_storage_file(upload.storage_key)
