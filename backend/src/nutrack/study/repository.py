from datetime import datetime

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from nutrack.courses.models import Course, CourseOffering
from nutrack.database import BaseRepository
from nutrack.enrollments.models import Enrollment
from nutrack.study.models import (
    MaterialCurationStatus,
    MockExam,
    MockExamAttempt,
    MockExamAttemptAnswer,
    MockExamQuestion,
    MockExamQuestionLink,
    MockExamAttemptStatus,
    StudyMaterialLibraryEntry,
    StudyMaterialUpload,
)


def _offering_loader():
    return joinedload(CourseOffering.course).load_only(
        Course.code,
        Course.level,
        Course.title,
    )


def _upload_loader():
    return (
        joinedload(StudyMaterialUpload.course_offering)
        .options(_offering_loader())
    )


def _library_loader():
    return (
        joinedload(StudyMaterialLibraryEntry.upload)
        .joinedload(StudyMaterialUpload.course_offering)
        .options(_offering_loader())
    )


class StudyMaterialUploadRepository(BaseRepository[StudyMaterialUpload]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudyMaterialUpload)

    async def get_enrolled_course(
        self,
        user_id: int,
        course_id: int,
    ) -> CourseOffering | None:
        stmt = (
            select(CourseOffering)
            .join(Enrollment, Enrollment.course_id == CourseOffering.id)
            .options(_offering_loader())
            .where(
                Enrollment.user_id == user_id,
                CourseOffering.id == course_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_upload_by_id(
        self,
        upload_id: int,
    ) -> StudyMaterialUpload | None:
        stmt = self._base_query().where(StudyMaterialUpload.id == upload_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_user_uploads(
        self,
        user_id: int,
        course_id: int,
    ) -> list[StudyMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                StudyMaterialUpload.uploader_id == user_id,
                StudyMaterialUpload.course_id == course_id,
            )
            .order_by(StudyMaterialUpload.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_admin_uploads(
        self,
        *,
        course_id: int | None = None,
        user_id: int | None = None,
        upload_status: str | None = None,
        curation_statuses: tuple[MaterialCurationStatus, ...],
    ) -> list[StudyMaterialUpload]:
        stmt = self._base_query().options(joinedload(StudyMaterialUpload.uploader))
        if course_id is not None:
            stmt = stmt.where(StudyMaterialUpload.course_id == course_id)
        if user_id is not None:
            stmt = stmt.where(StudyMaterialUpload.uploader_id == user_id)
        if upload_status is not None:
            stmt = stmt.where(StudyMaterialUpload.upload_status == upload_status)
        stmt = stmt.where(StudyMaterialUpload.curation_status.in_(curation_statuses))
        stmt = stmt.order_by(StudyMaterialUpload.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_stale_uploads(
        self,
        cutoff: datetime,
        statuses: tuple,
    ) -> list[StudyMaterialUpload]:
        stmt = (
            self._base_query()
            .where(
                StudyMaterialUpload.upload_status.in_(statuses),
                StudyMaterialUpload.updated_at < cutoff,
            )
            .order_by(StudyMaterialUpload.updated_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    def _base_query(self) -> Select[tuple[StudyMaterialUpload]]:
        return select(StudyMaterialUpload).options(
            _upload_loader(),
            joinedload(StudyMaterialUpload.library_entry),
        )


class StudyMaterialLibraryRepository(BaseRepository[StudyMaterialLibraryEntry]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, StudyMaterialLibraryEntry)

    async def list_course_library(
        self,
        course_id: int,
    ) -> list[StudyMaterialLibraryEntry]:
        stmt = (
            select(StudyMaterialLibraryEntry)
            .options(_library_loader())
            .where(StudyMaterialLibraryEntry.course_id == course_id)
            .order_by(
                StudyMaterialLibraryEntry.curated_week.asc(),
                StudyMaterialLibraryEntry.created_at.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_by_upload_id(
        self,
        upload_id: int,
    ) -> StudyMaterialLibraryEntry | None:
        stmt = (
            select(StudyMaterialLibraryEntry)
            .options(_library_loader())
            .where(StudyMaterialLibraryEntry.upload_id == upload_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


def _mock_exam_loader():
    return (
        joinedload(MockExam.course)
        .load_only(Course.code, Course.level, Course.title)
    )


def _question_offering_loader():
    return joinedload(MockExamQuestion.historical_course_offering).load_only(
        CourseOffering.id,
        CourseOffering.term,
        CourseOffering.year,
        CourseOffering.section,
        CourseOffering.meeting_time,
        CourseOffering.room,
    )


def _mock_exam_question_loader():
    return (
        selectinload(MockExam.question_links)
        .selectinload(MockExamQuestionLink.question)
        .options(_question_offering_loader())
    )


class MockExamRepository(BaseRepository[MockExam]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MockExam)

    async def get_by_id_with_links(self, mock_exam_id: int) -> MockExam | None:
        stmt = (
            select(MockExam)
            .options(
                _mock_exam_loader(),
                _mock_exam_question_loader(),
            )
            .where(MockExam.id == mock_exam_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_course(self, course_id: int) -> list[MockExam]:
        stmt = (
            select(MockExam)
            .options(_mock_exam_loader())
            .where(MockExam.course_id == course_id)
            .order_by(
                MockExam.assessment_type.asc(),
                MockExam.assessment_number.asc(),
                MockExam.version.desc(),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def list_matching_active(
        self,
        course_ids: list[int],
    ) -> list[MockExam]:
        if not course_ids:
            return []
        stmt = (
            select(MockExam)
            .options(_mock_exam_loader(), _mock_exam_question_loader())
            .where(MockExam.is_active.is_(True))
            .order_by(
                MockExam.course_id.asc(),
                MockExam.created_at.desc(),
            )
        )
        stmt = stmt.where(MockExam.course_id.in_(course_ids))
        result = await self.session.execute(stmt)
        return list(result.scalars().unique().all())

    async def get_latest_version(
        self,
        course_id: int,
        assessment_type: str,
        assessment_number: int,
    ) -> MockExam | None:
        stmt = (
            select(MockExam)
            .where(
                MockExam.course_id == course_id,
                MockExam.assessment_type == assessment_type,
                MockExam.assessment_number == assessment_number,
            )
            .order_by(MockExam.version.desc())
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_by_identity(
        self,
        course_id: int,
        assessment_type: str,
        assessment_number: int,
    ) -> MockExam | None:
        stmt = (
            select(MockExam)
            .options(_mock_exam_loader())
            .where(
                MockExam.course_id == course_id,
                MockExam.assessment_type == assessment_type,
                MockExam.assessment_number == assessment_number,
                MockExam.is_active.is_(True),
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def deactivate_family(
        self,
        course_id: int,
        assessment_type: str,
        assessment_number: int,
    ) -> None:
        stmt = (
            select(MockExam)
            .where(
                MockExam.course_id == course_id,
                MockExam.assessment_type == assessment_type,
                MockExam.assessment_number == assessment_number,
                MockExam.is_active.is_(True),
            )
        )
        result = await self.session.execute(stmt)
        for exam in result.scalars().all():
            exam.is_active = False
        await self.session.flush()

    async def count_attempts(self, mock_exam_id: int) -> int:
        stmt = select(func.count()).select_from(MockExamAttempt).where(
            MockExamAttempt.mock_exam_id == mock_exam_id
        )
        result = await self.session.execute(stmt)
        return int(result.scalar_one())


class MockExamQuestionRepository(BaseRepository[MockExamQuestion]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MockExamQuestion)

    async def list_by_course(self, course_id: int) -> list[MockExamQuestion]:
        stmt = (
            select(MockExamQuestion)
            .options(_question_offering_loader())
            .where(MockExamQuestion.course_id == course_id)
            .order_by(MockExamQuestion.updated_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def is_linked(self, question_id: int) -> bool:
        stmt = select(func.count()).select_from(MockExamQuestionLink).where(
            MockExamQuestionLink.question_id == question_id
        )
        result = await self.session.execute(stmt)
        return bool(result.scalar_one())

    async def usage_counts(self, question_ids: list[int]) -> dict[int, int]:
        if not question_ids:
            return {}
        stmt = (
            select(
                MockExamQuestionLink.question_id,
                func.count().label("usage_count"),
            )
            .where(MockExamQuestionLink.question_id.in_(question_ids))
            .group_by(MockExamQuestionLink.question_id)
        )
        result = await self.session.execute(stmt)
        return {qid: int(count) for qid, count in result.all()}


class MockExamAttemptRepository(BaseRepository[MockExamAttempt]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MockExamAttempt)

    async def get_active(self, user_id: int, mock_exam_id: int) -> MockExamAttempt | None:
        stmt = (
            select(MockExamAttempt)
            .where(
                MockExamAttempt.user_id == user_id,
                MockExamAttempt.mock_exam_id == mock_exam_id,
                MockExamAttempt.status == MockExamAttemptStatus.IN_PROGRESS,
            )
            .limit(1)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user_exam(
        self,
        user_id: int,
        mock_exam_id: int,
    ) -> list[MockExamAttempt]:
        stmt = (
            select(MockExamAttempt)
            .where(
                MockExamAttempt.user_id == user_id,
                MockExamAttempt.mock_exam_id == mock_exam_id,
            )
            .order_by(MockExamAttempt.started_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_user_exams(
        self,
        user_id: int,
        mock_exam_ids: list[int],
    ) -> list[MockExamAttempt]:
        if not mock_exam_ids:
            return []
        stmt = (
            select(MockExamAttempt)
            .where(
                MockExamAttempt.user_id == user_id,
                MockExamAttempt.mock_exam_id.in_(mock_exam_ids),
            )
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id_for_user(
        self,
        attempt_id: int,
        user_id: int,
    ) -> MockExamAttempt | None:
        stmt = (
            select(MockExamAttempt)
            .options(
                selectinload(MockExamAttempt.answers),
                joinedload(MockExamAttempt.mock_exam)
                .options(_mock_exam_loader(), _mock_exam_question_loader()),
            )
            .where(
                MockExamAttempt.id == attempt_id,
                MockExamAttempt.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, entity_id: int) -> MockExamAttempt | None:
        stmt = (
            select(MockExamAttempt)
            .options(
                selectinload(MockExamAttempt.answers),
                joinedload(MockExamAttempt.mock_exam)
                .options(_mock_exam_loader(), _mock_exam_question_loader()),
            )
            .where(MockExamAttempt.id == entity_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_attempt_stats(
        self,
        mock_exam_ids: list[int],
        user_id: int | None = None,
    ) -> dict[int, dict[str, float | int | bool | None]]:
        if not mock_exam_ids:
            return {}
        stmt = (
            select(MockExamAttempt)
            .where(MockExamAttempt.mock_exam_id.in_(mock_exam_ids))
        )
        if user_id is not None:
            stmt = stmt.where(MockExamAttempt.user_id == user_id)
        result = await self.session.execute(stmt)
        return _aggregate_attempt_stats(result.scalars().all())


class MockExamAttemptAnswerRepository(BaseRepository[MockExamAttemptAnswer]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, MockExamAttemptAnswer)

    async def get_by_attempt_and_link(
        self,
        attempt_id: int,
        link_id: int,
    ) -> MockExamAttemptAnswer | None:
        stmt = select(MockExamAttemptAnswer).where(
            MockExamAttemptAnswer.attempt_id == attempt_id,
            MockExamAttemptAnswer.mock_exam_question_link_id == link_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()


def _aggregate_attempt_stats(
    attempts: list[MockExamAttempt],
) -> dict[int, dict[str, float | int | bool | None]]:
    stats: dict[int, dict[str, float | int | bool | None]] = {}
    for attempt in attempts:
        current = stats.setdefault(
            attempt.mock_exam_id,
            {
                "attempts_count": 0,
                "best_score_pct": None,
                "average_score_pct": None,
                "latest_score_pct": None,
                "predicted_score_pct": None,
                "completed_attempts": 0,
                "has_active_attempt": False,
                "active_attempts": 0,
                "_latest_completed_at": None,
                "_completed_scores": [],
            },
        )
        current["attempts_count"] = int(current["attempts_count"]) + 1
        if attempt.status == MockExamAttemptStatus.IN_PROGRESS:
            current["has_active_attempt"] = True
            current["active_attempts"] = int(current["active_attempts"]) + 1
            continue
        if attempt.score_pct is None:
            continue
        score = float(attempt.score_pct)
        completed = int(current["completed_attempts"]) + 1
        total = float(current["average_score_pct"] or 0.0) * (completed - 1)
        current["completed_attempts"] = completed
        current["average_score_pct"] = round((total + score) / completed, 1)
        best = current["best_score_pct"]
        current["best_score_pct"] = score if best is None else max(float(best), score)
        submitted_at = attempt.submitted_at or attempt.started_at
        latest_at = current["_latest_completed_at"]
        if latest_at is None or submitted_at > latest_at:
            current["_latest_completed_at"] = submitted_at
            current["latest_score_pct"] = score
        current["_completed_scores"].append((submitted_at, score))
    for current in stats.values():
        completed = sorted(
            current["_completed_scores"],
            key=lambda item: item[0],
            reverse=True,
        )
        latest_scores = [score for _, score in completed[:3]]
        if latest_scores:
            current["predicted_score_pct"] = round(
                sum(latest_scores) / len(latest_scores),
                1,
            )
        current.pop("_latest_completed_at", None)
        current.pop("_completed_scores", None)
    return stats
