from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.assessments.exceptions import AssessmentConflictError
from nutrack.assessments.models import AssessmentType
from nutrack.assessments.schemas import CreateAssessmentRequest, UpdateAssessmentRequest
from nutrack.assessments.service import AssessmentService


def _assessment_record(
    *,
    assessment_id: int = 7,
    assessment_type: AssessmentType = AssessmentType.MIDTERM,
    assessment_number: int = 2,
):
    return SimpleNamespace(
        id=assessment_id,
        user_id=1,
        course_id=4,
        assessment_type=assessment_type,
        assessment_number=assessment_number,
        description="Focus on chapters 1-4",
        deadline=datetime(2026, 4, 20, tzinfo=timezone.utc),
        weight=25.0,
        score=None,
        max_score=100.0,
        is_completed=False,
        created_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 2, tzinfo=timezone.utc),
        course_offering=SimpleNamespace(
            course=SimpleNamespace(code="BIOL", level="101", title="Introductory Biology")
        ),
    )


@pytest.mark.asyncio
async def test_create_assessment_uses_assessment_number() -> None:
    assessment_repo = SimpleNamespace(
        get_by_identity=AsyncMock(return_value=None),
        create=AsyncMock(return_value=SimpleNamespace(id=7)),
        get_by_id_and_user=AsyncMock(return_value=_assessment_record()),
    )
    enrollment_repo = SimpleNamespace(session=AsyncMock())
    service = AssessmentService(assessment_repo, enrollment_repo)
    service._is_enrolled = AsyncMock(return_value=True)  # noqa: SLF001
    service._schedule_mock_exam_generation = AsyncMock()  # noqa: SLF001
    payload = CreateAssessmentRequest(
        course_id=4,
        assessment_type=AssessmentType.MIDTERM,
        assessment_number=2,
        deadline=datetime(2026, 4, 20, tzinfo=timezone.utc),
        weight=25,
        max_score=100,
        description="Focus on chapters 1-4",
    )

    result = await service.create_assessment(1, payload)

    assert result.assessment_number == 2
    assert result.title == "Midterm 2"
    service._schedule_mock_exam_generation.assert_awaited_once()  # noqa: SLF001
    assessment_repo.create.assert_awaited_once_with(
        user_id=1,
        course_id=4,
        assessment_type=AssessmentType.MIDTERM,
        assessment_number=2,
        description="Focus on chapters 1-4",
        deadline=datetime(2026, 4, 20, tzinfo=timezone.utc),
        weight=25.0,
        max_score=100.0,
        score=None,
        is_completed=False,
    )


@pytest.mark.asyncio
async def test_generate_mock_exam_queues_job() -> None:
    assessment = _assessment_record()
    assessment_repo = SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=assessment),
    )
    enrollment_repo = SimpleNamespace(session=AsyncMock())
    service = AssessmentService(assessment_repo, enrollment_repo)
    service._queue_manual_mock_exam_generation = AsyncMock(  # noqa: SLF001
        return_value=SimpleNamespace(id=31)
    )

    result = await service.generate_mock_exam(1, 7)

    assert result.job_id == 31
    assert result.status == "queued"


@pytest.mark.asyncio
async def test_update_assessment_rejects_duplicate_identity() -> None:
    current = _assessment_record(assessment_id=7)
    duplicate = _assessment_record(assessment_id=8)
    assessment_repo = SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=current),
        get_by_identity=AsyncMock(return_value=duplicate),
    )
    enrollment_repo = SimpleNamespace(session=AsyncMock())
    service = AssessmentService(assessment_repo, enrollment_repo)
    payload = UpdateAssessmentRequest(
        assessment_type=AssessmentType.MIDTERM,
        assessment_number=2,
    )

    with pytest.raises(AssessmentConflictError):
        await service.update_assessment(1, 7, payload)
