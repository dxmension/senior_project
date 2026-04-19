from types import SimpleNamespace
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock

import pytest

from nutrack.assessments.models import AssessmentType
from nutrack.course_materials.models import MaterialUploadStatus
from nutrack.mock_exams.generation import (
    MockExamGenerationService,
    WriteQuestionPoolArgs,
    _tool_spec,
)
from nutrack.mock_exams.models import MockExamGenerationTrigger


@pytest.mark.asyncio
async def test_ensure_setting_rows_inherits_default_model() -> None:
    service = MockExamGenerationService(session=AsyncMock())
    created_rows: list[dict] = []

    async def create_row(**payload):
        created_rows.append(payload)
        return SimpleNamespace(**payload)

    service.settings_repo = SimpleNamespace(
        list_all=AsyncMock(return_value=[]),
        create=AsyncMock(side_effect=create_row),
    )

    rows = await service._ensure_setting_rows()  # noqa: SLF001

    assert rows["quiz"].model == "gpt-5-mini"
    assert rows["midterm"].model == "gpt-5-mini"
    assert rows["final"].model == "gpt-5-mini"
    assert created_rows[1]["model"] == "gpt-5-mini"


@pytest.mark.asyncio
async def test_get_effective_settings_uses_override_values() -> None:
    service = MockExamGenerationService(session=AsyncMock())
    default_row = SimpleNamespace(
        setting_key="default",
        assessment_type=None,
        enabled=True,
        model="gpt-5-mini",
        temperature=0.2,
        question_count=20,
        time_limit_minutes=40,
        max_source_files=6,
        max_source_chars=24000,
        regeneration_offset_hours=24,
        new_question_ratio=0.5,
        tricky_question_ratio=0.3,
    )
    quiz_row = SimpleNamespace(
        **{
            **default_row.__dict__,
            "setting_key": "quiz",
            "assessment_type": AssessmentType.QUIZ,
            "question_count": 12,
            "time_limit_minutes": 20,
        }
    )
    service._ensure_setting_rows = AsyncMock(  # noqa: SLF001
        return_value={"default": default_row, "quiz": quiz_row}
    )

    settings = await service.get_effective_settings(AssessmentType.QUIZ)

    assert settings.model == "gpt-5-mini"
    assert settings.question_count == 12
    assert settings.time_limit_minutes == 20


@pytest.mark.asyncio
async def test_ensure_setting_rows_normalizes_invalid_model_alias() -> None:
    service = MockExamGenerationService(session=AsyncMock())
    existing = SimpleNamespace(
        setting_key="default",
        model="gpt-5.1-mini",
    )

    async def update_row(row, **payload):
        data = dict(row.__dict__)
        data.update(payload)
        return SimpleNamespace(**data)

    service.settings_repo = SimpleNamespace(
        list_all=AsyncMock(return_value=[existing]),
        update=AsyncMock(side_effect=update_row),
        create=AsyncMock(),
    )

    rows = await service._ensure_setting_rows()  # noqa: SLF001

    assert rows["default"].model == "gpt-5-mini"
    service.settings_repo.update.assert_awaited()


@pytest.mark.asyncio
async def test_eligible_uploads_uses_private_library_only() -> None:
    service = MockExamGenerationService(session=AsyncMock())
    upload_1 = SimpleNamespace(
        id=2,
        user_week=2,
        created_at=2,
        upload_status=MaterialUploadStatus.COMPLETED,
    )
    upload_2 = SimpleNamespace(
        id=1,
        user_week=1,
        created_at=1,
        upload_status=MaterialUploadStatus.COMPLETED,
    )
    upload_failed = SimpleNamespace(
        id=3,
        user_week=3,
        created_at=3,
        upload_status=MaterialUploadStatus.FAILED,
    )
    service.upload_repo = SimpleNamespace(
        list_user_uploads=AsyncMock(
            return_value=[upload_1, upload_2, upload_failed]
        )
    )

    uploads = await service._eligible_uploads(1, 4)  # noqa: SLF001

    assert [item.id for item in uploads] == [1, 2]


@pytest.mark.asyncio
async def test_generate_returns_private_material_skip_reason_when_none() -> None:
    service = MockExamGenerationService(session=AsyncMock())
    assessment = SimpleNamespace(
        id=7,
        is_completed=False,
        assessment_type=AssessmentType.QUIZ,
        user_id=1,
        course_id=4,
    )
    job = SimpleNamespace(assessment_id=7)
    service.assessment_repo = SimpleNamespace(get_by_id=AsyncMock(return_value=assessment))
    service.get_effective_settings = AsyncMock(
        return_value=SimpleNamespace(enabled=True)
    )
    service._material_context = AsyncMock(  # noqa: SLF001
        return_value=SimpleNamespace(uploads=[], text="")
    )

    exam, reason = await service._generate(job)  # noqa: SLF001

    assert exam is None
    assert reason == "no_private_materials"


@pytest.mark.asyncio
async def test_schedule_for_assessment_creates_deadline_job_without_uploads() -> None:
    service = MockExamGenerationService(session=AsyncMock())
    assessment = SimpleNamespace(
        id=7,
        deadline=datetime.now(timezone.utc) + timedelta(days=3),
        assessment_type=AssessmentType.QUIZ,
    )
    service.job_repo = SimpleNamespace(
        cancel_pending_for_assessment=AsyncMock(),
    )
    service.get_effective_settings = AsyncMock(
        return_value=SimpleNamespace(regeneration_offset_hours=24)
    )
    service._create_job = AsyncMock(  # noqa: SLF001
        return_value=SimpleNamespace(
            id=11,
            trigger=MockExamGenerationTrigger.DEADLINE_REMINDER,
        )
    )

    jobs = await service.schedule_for_assessment(assessment)

    assert len(jobs) == 1
    assert jobs[0].trigger == MockExamGenerationTrigger.DEADLINE_REMINDER


def test_tool_schema_closes_nested_objects() -> None:
    spec = _tool_spec(
        "write_question_pool",
        "Persist newly created AI questions for the target user.",
        WriteQuestionPoolArgs,
    )
    schema = spec["parameters"]

    assert schema["additionalProperties"] is False
    assert schema["required"] == ["questions"]
    nested = schema["$defs"]["GeneratedQuestionInput"]
    assert nested["additionalProperties"] is False
    assert nested["required"] == [
        "question_text",
        "answer_variant_1",
        "answer_variant_2",
        "answer_variant_3",
        "answer_variant_4",
        "answer_variant_5",
        "answer_variant_6",
        "correct_option_index",
        "explanation",
    ]
