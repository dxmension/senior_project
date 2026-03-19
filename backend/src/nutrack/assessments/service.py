from sqlalchemy import exists, select

from nutrack.assessments.exceptions import (
    AssessmentNotEnrolledError,
    AssessmentNotFoundError,
)
from nutrack.assessments.models import Assessment
from nutrack.assessments.repository import AssessmentRepository
from nutrack.assessments.schemas import (
    AssessmentResponse,
    CreateAssessmentRequest,
    UpdateAssessmentRequest,
)
from nutrack.enrollments.models import Enrollment
from nutrack.enrollments.repository import EnrollmentRepository


def _build_response(assessment: Assessment) -> AssessmentResponse:
    course = assessment.course_offering.course
    level = (course.level or "").strip()
    course_code = f"{course.code} {level}" if level and level != "0" else course.code
    return AssessmentResponse(
        id=assessment.id,
        course_id=assessment.course_id,
        course_code=course_code,
        course_title=course.title,
        assessment_type=assessment.assessment_type,
        title=assessment.title,
        description=assessment.description,
        deadline=assessment.deadline,
        weight=assessment.weight,
        score=assessment.score,
        max_score=assessment.max_score,
        is_completed=assessment.is_completed,
        created_at=assessment.created_at,
        updated_at=assessment.updated_at,
    )


class AssessmentService:
    def __init__(
        self,
        assessment_repo: AssessmentRepository,
        enrollment_repo: EnrollmentRepository,
    ) -> None:
        self.assessment_repo = assessment_repo
        self.enrollment_repo = enrollment_repo

    async def list_assessments(
        self,
        user_id: int,
        *,
        course_id: int | None = None,
        upcoming_only: bool = False,
        completed: bool | None = None,
    ) -> list[AssessmentResponse]:
        assessments = await self.assessment_repo.get_by_user(
            user_id,
            course_id=course_id,
            upcoming_only=upcoming_only,
            completed=completed,
        )
        return [_build_response(a) for a in assessments]

    async def create_assessment(
        self,
        user_id: int,
        data: CreateAssessmentRequest,
    ) -> AssessmentResponse:
        if not await self._is_enrolled(user_id, data.course_id):
            raise AssessmentNotEnrolledError()
        assessment = await self.assessment_repo.create(
            user_id=user_id,
            course_id=data.course_id,
            assessment_type=data.assessment_type,
            title=data.title,
            description=data.description,
            deadline=data.deadline,
            weight=data.weight,
            max_score=data.max_score,
            score=None,
            is_completed=False,
        )
        loaded = await self.assessment_repo.get_by_id_and_user(assessment.id, user_id)
        return _build_response(loaded)

    async def get_assessment(
        self,
        user_id: int,
        assessment_id: int,
    ) -> AssessmentResponse:
        assessment = await self.assessment_repo.get_by_id_and_user(
            assessment_id, user_id
        )
        if not assessment:
            raise AssessmentNotFoundError()
        return _build_response(assessment)

    async def update_assessment(
        self,
        user_id: int,
        assessment_id: int,
        data: UpdateAssessmentRequest,
    ) -> AssessmentResponse:
        assessment = await self.assessment_repo.get_by_id_and_user(
            assessment_id, user_id
        )
        if not assessment:
            raise AssessmentNotFoundError()
        updates = {field: getattr(data, field) for field in data.model_fields_set}
        if updates:
            await self.assessment_repo.update(assessment, **updates)
        refreshed = await self.assessment_repo.get_by_id_and_user(assessment_id, user_id)
        return _build_response(refreshed)

    async def delete_assessment(
        self,
        user_id: int,
        assessment_id: int,
    ) -> None:
        deleted = await self.assessment_repo.delete_by_id_and_user(
            assessment_id, user_id
        )
        if not deleted:
            raise AssessmentNotFoundError()

    async def _is_enrolled(self, user_id: int, course_id: int) -> bool:
        # course_id is a course_offerings.id; Enrollment.course_id also references course_offerings.id
        stmt = select(
            exists().where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )
        result = await self.enrollment_repo.session.execute(stmt)
        return bool(result.scalar())
