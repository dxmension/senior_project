from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from nutrack.mock_exams import tasks


class _AsyncSessionContext:
    def __init__(self, session) -> None:
        self._session = session

    async def __aenter__(self):
        return self._session

    async def __aexit__(self, exc_type, exc, tb):
        return False


@pytest.mark.asyncio
async def test_run_generation_updates_task_id_and_runs_job(monkeypatch) -> None:
    session = SimpleNamespace(commit=AsyncMock())
    job = SimpleNamespace(
        status=SimpleNamespace(value="completed"),
        error_message=None,
        generated_mock_exam_id=21,
    )
    service = SimpleNamespace(
        set_celery_task_id=AsyncMock(),
        run_job=AsyncMock(return_value=job),
    )

    monkeypatch.setattr(
        tasks,
        "AsyncSessionLocal",
        lambda: _AsyncSessionContext(session),
    )
    monkeypatch.setattr(
        tasks,
        "MockExamGenerationService",
        lambda session: service,
    )

    await tasks._run_generation(7, "task-7")

    service.set_celery_task_id.assert_awaited_once_with(7, "task-7")
    service.run_job.assert_awaited_once_with(7)
    session.commit.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_reset_job_marks_job_queued(monkeypatch) -> None:
    session = SimpleNamespace(commit=AsyncMock())
    service = SimpleNamespace(reset_job_to_queued=AsyncMock())

    monkeypatch.setattr(
        tasks,
        "AsyncSessionLocal",
        lambda: _AsyncSessionContext(session),
    )
    monkeypatch.setattr(
        tasks,
        "MockExamGenerationService",
        lambda session: service,
    )

    await tasks._reset_job(7, "boom", "task-7")

    service.reset_job_to_queued.assert_awaited_once_with(7, "boom", "task-7")
    session.commit.assert_awaited_once_with()


def test_generate_task_retries_and_resets_job(monkeypatch) -> None:
    run_error = RuntimeError("boom")
    retry_error = RuntimeError("retrying")
    retry_mock = Mock(side_effect=retry_error)
    task_self = SimpleNamespace(
        request=SimpleNamespace(id="task-7", retries=0),
        max_retries=2,
        retry=retry_mock,
    )

    monkeypatch.setattr(
        tasks,
        "_run_generation",
        Mock(return_value=object()),
    )
    monkeypatch.setattr(
        tasks,
        "_reset_job",
        Mock(return_value=object()),
    )

    calls = {"count": 0}

    def fake_asyncio_run(coro):
        calls["count"] += 1
        if calls["count"] == 1:
            raise run_error
        return None

    monkeypatch.setattr(tasks.asyncio, "run", fake_asyncio_run)

    with pytest.raises(RuntimeError, match="retrying"):
        tasks.generate_assessment_mock_exam_task.run.__func__(task_self, 7)

    retry_mock.assert_called_once()
    assert calls["count"] == 2


def test_generate_task_raises_after_max_retries(monkeypatch) -> None:
    run_error = RuntimeError("boom")
    retry_mock = Mock()
    task_self = SimpleNamespace(
        request=SimpleNamespace(id="task-7", retries=2),
        max_retries=2,
        retry=retry_mock,
    )

    monkeypatch.setattr(
        tasks.asyncio,
        "run",
        Mock(side_effect=run_error),
    )

    with pytest.raises(RuntimeError, match="boom"):
        tasks.generate_assessment_mock_exam_task.run.__func__(task_self, 7)

    retry_mock.assert_not_called()
