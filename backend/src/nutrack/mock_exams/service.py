import re
from math import ceil
from datetime import datetime, timezone
from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from nutrack.assessments.models import Assessment
from nutrack.assessments.repository import AssessmentRepository
from nutrack.assessments.utils import assessment_label, mock_exam_title
from nutrack.courses.models import CourseOffering
from nutrack.enrollments.models import EnrollmentStatus
from nutrack.enrollments.repository import EnrollmentRepository
from nutrack.mock_exams.exceptions import (
    MockExamAttemptNotFoundError,
    MockExamForbiddenError,
    MockExamNotFoundError,
    MockExamQuestionNotFoundError,
    MockExamValidationError,
)
from nutrack.mock_exams.models import (
    MockExam,
    MockExamAttempt,
    MockExamAttemptStatus,
    MockExamQuestion,
    MockExamQuestionLink,
    MockExamQuestionSource,
)
from nutrack.mock_exams.repository import (
    MockExamAttemptAnswerRepository,
    MockExamAttemptRepository,
    MockExamQuestionRepository,
    MockExamRepository,
)
from nutrack.mock_exams.utils import predicted_grade_letter, predicted_score_average
from nutrack.storage import slugify

ELIGIBLE_ASSESSMENT_TYPES = {"quiz", "midterm", "final"}


def format_course_code(code: str, level: str) -> str:
    return f"{code} {level}".strip() if level and level != "0" else code


def _attempt_completed_at(attempt: MockExamAttempt) -> datetime:
    return attempt.submitted_at or attempt.started_at


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


def _attempt_status_value(attempt: MockExamAttempt) -> str:
    status = attempt.status
    return status.value if hasattr(status, "value") else str(status)


def _attempt_expires_at(
    started_at: datetime,
    time_limit_minutes: int | None,
) -> datetime | None:
    if time_limit_minutes is None:
        return None
    return started_at + timedelta(minutes=time_limit_minutes)


def _remaining_seconds(expires_at: datetime, now: datetime) -> int:
    seconds = (expires_at - now).total_seconds()
    return max(int(ceil(seconds)), 0)


def _attempt_response(
    attempt: MockExamAttempt,
    time_limit_minutes: int | None = None,
    now: datetime | None = None,
) -> dict:
    expires_at = None
    remaining_seconds = None
    status = _attempt_status_value(attempt)
    if status == MockExamAttemptStatus.IN_PROGRESS.value:
        expires_at = _attempt_expires_at(attempt.started_at, time_limit_minutes)
        if expires_at is not None:
            remaining_seconds = _remaining_seconds(
                expires_at,
                now or datetime.now(timezone.utc),
            )
    return {
        "id": attempt.id,
        "status": status,
        "started_at": attempt.started_at,
        "submitted_at": attempt.submitted_at,
        "expires_at": expires_at,
        "remaining_seconds": remaining_seconds,
        "last_active_at": getattr(attempt, "last_active_at", attempt.started_at),
        "current_position": getattr(attempt, "current_position", 1),
        "answered_count": getattr(attempt, "answered_count", 0),
        "correct_count": getattr(attempt, "correct_count", 0),
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


class MockExamService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.assessment_repo = AssessmentRepository(session)
        self.enrollment_repo = EnrollmentRepository(session)
        self.mock_exam_repo = MockExamRepository(session)
        self.mock_exam_question_repo = MockExamQuestionRepository(session)
        self.mock_exam_attempt_repo = MockExamAttemptRepository(session)
        self.mock_exam_answer_repo = MockExamAttemptAnswerRepository(session)

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
        active_attempts = await self._sync_active_attempts(user_id, available)
        stats_map = await self._student_attempt_stats(user_id, available)
        prediction_map = await self._student_prediction_map(user_id, available)
        return self._group_mock_exam_items(
            courses,
            available,
            stats_map,
            prediction_map,
            active_attempts,
        )

    async def get_mock_exam_dashboard(self, user_id: int, mock_exam_id: int) -> dict:
        exam = await self._require_student_exam_access(user_id, mock_exam_id)
        attempts = await self.mock_exam_attempt_repo.list_for_user_exam(user_id, exam.id)
        await self._sync_attempts_for_exam(attempts, exam)
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
            await self._sync_attempt_timeout(active, exam)
            if _attempt_status_value(active) == MockExamAttemptStatus.IN_PROGRESS.value:
                return _attempt_response(active, exam.time_limit_minutes)
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
        return _attempt_response(attempt, exam.time_limit_minutes, now)

    async def get_mock_exam_attempt(
        self,
        user_id: int,
        attempt_id: int,
    ) -> dict:
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        await self._sync_attempt_timeout(attempt, attempt.mock_exam)
        return self._attempt_session_payload(attempt)

    async def get_mock_exam_attempt_review(
        self,
        user_id: int,
        attempt_id: int,
    ) -> dict:
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        await self._sync_attempt_timeout(attempt, attempt.mock_exam)
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
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        exam = await self.mock_exam_repo.get_by_id_with_links(attempt.mock_exam_id)
        await self._sync_attempt_timeout(attempt, exam)
        if _attempt_status_value(attempt) != MockExamAttemptStatus.IN_PROGRESS.value:
            return _attempt_response(attempt, exam.time_limit_minutes)
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
        return _attempt_response(attempt, exam.time_limit_minutes)

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
        await self._validated_questions(payload.course_id, payload.questions)
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

    async def update_mock_exam_question(self, question_id: int, payload) -> dict:
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

    async def _sync_active_attempts(
        self,
        user_id: int,
        exams: list[MockExam],
    ) -> dict[int, MockExamAttempt]:
        exam_ids = [exam.id for exam in exams]
        attempts = await self.mock_exam_attempt_repo.list_active_for_user_exams(
            user_id,
            exam_ids,
        )
        exam_map = {exam.id: exam for exam in exams}
        for attempt in attempts:
            exam = exam_map.get(attempt.mock_exam_id)
            if exam is not None:
                await self._sync_attempt_timeout(attempt, exam)
        return {
            attempt.mock_exam_id: attempt
            for attempt in attempts
            if _attempt_status_value(attempt) == MockExamAttemptStatus.IN_PROGRESS.value
        }

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

    def _recent_prediction_scores(self, scores_map: dict) -> dict:
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
        active_attempts: dict[int, MockExamAttempt],
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
                    "active_attempt": self._attempt_summary(
                        active_attempts[exam.id],
                        exam.time_limit_minutes,
                    )
                    if exam.id in active_attempts
                    else None,
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
        active = next(
            (
                item
                for item in attempts
                if _attempt_status_value(item) == MockExamAttemptStatus.IN_PROGRESS.value
            ),
            None,
        )
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
            "attempts_count": len(attempts),
            "best_score_pct": best,
            "average_score_pct": average,
            "latest_score_pct": latest,
            "predicted_score_pct": predicted,
            "predicted_grade_letter": predicted_grade_letter(predicted),
            "improvement_pct": improvement,
            "active_attempt": _attempt_response(active, exam.time_limit_minutes) if active else None,
            "attempts": [
                self._attempt_summary(item, exam.time_limit_minutes)
                for item in attempts
            ],
            "trend": self._trend_points(completed),
        }

    def _attempt_session_payload(self, attempt: MockExamAttempt) -> dict:
        exam = attempt.mock_exam
        answers = [self._answer_payload(answer) for answer in attempt.answers]
        return {
            **_attempt_response(attempt, exam.time_limit_minutes),
            **self._attempt_exam_payload(exam),
            "questions": self._student_question_links_payload(exam),
            "answers": answers,
        }

    def _attempt_review_payload(self, attempt: MockExamAttempt) -> dict:
        exam = attempt.mock_exam
        answers = {item.mock_exam_question_link_id: item for item in attempt.answers}
        questions = self._review_questions_payload(exam, answers)
        return {
            **_attempt_response(attempt, exam.time_limit_minutes),
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

    def _attempt_summary(
        self,
        attempt: MockExamAttempt,
        time_limit_minutes: int | None,
    ) -> dict:
        payload = _attempt_response(attempt, time_limit_minutes)
        return {
            "id": payload["id"],
            "status": payload["status"],
            "score_pct": payload["score_pct"],
            "started_at": payload["started_at"],
            "submitted_at": payload["submitted_at"],
            "expires_at": payload["expires_at"],
            "remaining_seconds": payload["remaining_seconds"],
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

    def _review_questions_payload(self, exam: MockExam, answers: dict[int, object]) -> list[dict]:
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

    async def _sync_attempts_for_exam(
        self,
        attempts: list[MockExamAttempt],
        exam: MockExam,
    ) -> None:
        for attempt in attempts:
            await self._sync_attempt_timeout(attempt, exam)

    async def _sync_attempt_timeout(
        self,
        attempt: MockExamAttempt,
        exam: MockExam,
    ) -> bool:
        if _attempt_status_value(attempt) != MockExamAttemptStatus.IN_PROGRESS.value:
            return False
        expires_at = _attempt_expires_at(attempt.started_at, exam.time_limit_minutes)
        now = datetime.now(timezone.utc)
        if expires_at is None or expires_at > now:
            return False
        await self._complete_attempt(attempt.id, exam, expires_at)
        return True

    async def _complete_attempt(
        self,
        attempt_id: int,
        exam: MockExam,
        submitted_at: datetime,
    ) -> MockExamAttempt:
        attempt = await self.mock_exam_attempt_repo.get_by_id(attempt_id)
        if attempt is None:
            raise MockExamAttemptNotFoundError()
        if _attempt_status_value(attempt) != MockExamAttemptStatus.IN_PROGRESS.value:
            return attempt
        answered_count, correct_count, current_position = self._attempt_progress(
            attempt.answers,
            exam,
        )
        total = max(len(exam.question_links), 1)
        score_pct = round(correct_count / total * 100, 1)
        return await self.mock_exam_attempt_repo.update(
            attempt,
            status=MockExamAttemptStatus.COMPLETED,
            submitted_at=submitted_at,
            last_active_at=submitted_at,
            answered_count=answered_count,
            correct_count=correct_count,
            current_position=current_position,
            score_pct=score_pct,
        )

    def _attempt_progress(
        self,
        answers: list,
        exam: MockExam,
    ) -> tuple[int, int, int]:
        link_positions = {link.id: link.position for link in exam.question_links}
        answered = [
            item for item in answers if item.selected_option_index is not None
        ]
        correct_count = len([item for item in answered if item.is_correct])
        current_position = 1
        positions = [
            link_positions[item.mock_exam_question_link_id]
            for item in answered
            if item.mock_exam_question_link_id in link_positions
        ]
        if positions:
            current_position = min(max(positions) + 1, len(exam.question_links))
        return len(answered), correct_count, max(current_position, 1)

    async def _require_active_attempt(
        self,
        user_id: int,
        attempt_id: int,
    ) -> MockExamAttempt:
        attempt = await self.mock_exam_attempt_repo.get_by_id_for_user(attempt_id, user_id)
        if not attempt:
            raise MockExamAttemptNotFoundError()
        expired = await self._sync_attempt_timeout(attempt, attempt.mock_exam)
        if _attempt_status_value(attempt) != MockExamAttemptStatus.IN_PROGRESS.value:
            if expired:
                raise MockExamValidationError("Mock exam time limit has expired")
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
        answered_count, correct_count, current_position = self._attempt_progress(
            refreshed.answers,
            exam,
        )
        await self.mock_exam_attempt_repo.update(
            attempt,
            answered_count=answered_count,
            correct_count=correct_count,
            current_position=current_position,
            last_active_at=datetime.now(timezone.utc),
        )

    async def _validated_questions(
        self,
        course_id: int,
        questions: list,
    ) -> dict[int, MockExamQuestion]:
        payload: dict[int, MockExamQuestion] = {}
        for item in questions:
            question = await self.mock_exam_question_repo.get_by_id(item.question_id)
            if not question:
                raise MockExamQuestionNotFoundError()
            if question.course_id != course_id:
                raise MockExamValidationError("Question does not belong to the selected course")
            payload[item.question_id] = question
        return payload

    async def _create_question_links(self, mock_exam_id: int, items: list) -> None:
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
        data.answer_variant_3 = (
            payload.answer_variant_3
            if payload.answer_variant_3 is not None
            else question.answer_variant_3
        )
        data.answer_variant_4 = (
            payload.answer_variant_4
            if payload.answer_variant_4 is not None
            else question.answer_variant_4
        )
        data.answer_variant_5 = (
            payload.answer_variant_5
            if payload.answer_variant_5 is not None
            else question.answer_variant_5
        )
        data.answer_variant_6 = (
            payload.answer_variant_6
            if payload.answer_variant_6 is not None
            else question.answer_variant_6
        )
        data.correct_option_index = payload.correct_option_index or question.correct_option_index
        data.explanation = (
            payload.explanation
            if payload.explanation is not None
            else question.explanation
        )
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
