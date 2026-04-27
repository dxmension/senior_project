from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.assessments.models import AssessmentType
from nutrack.assessments.schemas import UpdateAssessmentRequest
from nutrack.assessments.service import AssessmentService


def _assessment() -> SimpleNamespace:
    return SimpleNamespace(
        id=7,
        user_id=1,
        course_id=4,
        assessment_type=AssessmentType.MIDTERM,
        assessment_number=2,
        description="Focus on chapters 1-4",
        deadline=datetime(2026, 4, 20, tzinfo=timezone.utc),
        weight=25.0,
        score=None,
        max_score=100.0,
        is_completed=False,
        created_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        updated_at=datetime(2026, 4, 2, tzinfo=timezone.utc),
        course_offering=SimpleNamespace(
            course=SimpleNamespace(code="BIOL", level="101", title="Biology")
        ),
    )


@pytest.mark.asyncio
async def test_update_assessment_reschedules_mock_exam_generation() -> None:
    assessment = _assessment()
    assessment_repo = SimpleNamespace(
        get_by_id_and_user=AsyncMock(side_effect=[assessment, assessment]),
        get_by_identity=AsyncMock(return_value=None),
        update=AsyncMock(),
    )
    enrollment_repo = SimpleNamespace(session=AsyncMock())
    service = AssessmentService(assessment_repo, enrollment_repo)
    service._schedule_mock_exam_generation = AsyncMock()  # noqa: SLF001
    payload = UpdateAssessmentRequest(description="Updated")

    await service.update_assessment(1, 7, payload)

    service._schedule_mock_exam_generation.assert_awaited_once_with(assessment)  # noqa: SLF001


@pytest.mark.asyncio
async def test_delete_assessment_cancels_mock_exam_generation() -> None:
    assessment = _assessment()
    assessment_repo = SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=assessment),
        delete_by_id_and_user=AsyncMock(return_value=True),
    )
    enrollment_repo = SimpleNamespace(session=AsyncMock())
    service = AssessmentService(assessment_repo, enrollment_repo)
    service._cancel_mock_exam_generation = AsyncMock()  # noqa: SLF001

    await service.delete_assessment(1, 7)

    service._cancel_mock_exam_generation.assert_awaited_once_with(7)  # noqa: SLF001
    assessment_repo.delete_by_id_and_user.assert_awaited_once_with(7, 1)


@pytest.mark.asyncio
async def test_schedule_mock_exam_generation_stores_celery_task_ids(monkeypatch) -> None:
    session = AsyncMock()
    assessment_repo = SimpleNamespace(session=session)
    enrollment_repo = SimpleNamespace(session=session)
    service = AssessmentService(assessment_repo, enrollment_repo)
    assessment = _assessment()
    jobs = [SimpleNamespace(id=11), SimpleNamespace(id=12)]
    generation_service = SimpleNamespace(
        schedule_for_assessment=AsyncMock(return_value=(jobs, [])),
        set_celery_task_id=AsyncMock(),
    )

    monkeypatch.setattr(
        "nutrack.mock_exams.generation.MockExamGenerationService",
        lambda _session: generation_service,
    )
    monkeypatch.setattr(
        "nutrack.assessments.service._revoke_tasks",
        lambda task_ids: None,
    )
    service._enqueue_generation_job = lambda job: f"task-{job.id}"  # noqa: SLF001

    await service._schedule_mock_exam_generation(  # noqa: SLF001
        assessment,
    )

    generation_service.schedule_for_assessment.assert_awaited_once()
    assert generation_service.set_celery_task_id.await_args_list[0].args == (11, "task-11")
    assert generation_service.set_celery_task_id.await_args_list[1].args == (12, "task-12")
