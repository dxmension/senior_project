from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from nutrack.mindmaps.exceptions import (
    MindmapGenerationError,
    MindmapUnavailableError,
)
from nutrack.mindmaps.schemas import (
    GenerateMindmapRequest,
    MindmapGenerationStatusResponse,
    MindmapLLMNode,
    MindmapLLMResponse,
)
from nutrack.mindmaps.service import MindmapService
from nutrack.tools.llm.exceptions import LLMConfigurationError, LLMResponseError
from nutrack.mindmaps import service as mindmap_service


@pytest.mark.asyncio
async def test_generate_and_save_maps_flat_nodes_to_tree(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parsed = MindmapLLMResponse(
        root_id="root",
        nodes=[
            MindmapLLMNode(
                id="root",
                label="Cell Biology",
                description="Root description.",
                child_ids=["membrane"],
            ),
            MindmapLLMNode(
                id="membrane",
                label="Cell Membranes",
                description="Membrane description.",
                parent_id="root",
                child_ids=["transport"],
            ),
            MindmapLLMNode(
                id="transport",
                label="Membrane Transport",
                description="Transport description.",
                parent_id="membrane",
            ),
        ],
    )
    monkeypatch.setattr(
        mindmap_service,
        "parse_structured_response",
        AsyncMock(return_value=parsed),
    )
    repo = SimpleNamespace(create=AsyncMock(side_effect=_create_mindmap))
    material_repo = SimpleNamespace(
        list_completed_uploads_for_week=AsyncMock(return_value=[]),
    )
    service = MindmapService(repo=repo, material_repo=material_repo, storage=object())

    result = await service.generate_and_save(
        user_id=1,
        course_id=2,
        request=GenerateMindmapRequest(week=3, depth=3),
    )

    assert result.topic == "Cell Biology"
    assert result.root.label == "Cell Biology"
    assert len(result.root.children) == 1
    assert result.root.children[0].label == "Cell Membranes"
    assert result.root.children[0].children[0].label == "Membrane Transport"
    assert result.root.id != result.root.children[0].id


@pytest.mark.asyncio
async def test_generate_and_save_translates_missing_api_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mindmap_service,
        "parse_structured_response",
        AsyncMock(side_effect=LLMConfigurationError("missing key")),
    )
    service = _service()

    with pytest.raises(MindmapUnavailableError):
        await service.generate_and_save(
            user_id=1,
            course_id=2,
            request=GenerateMindmapRequest(week=2, depth=2),
        )


@pytest.mark.asyncio
async def test_generate_and_save_translates_llm_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        mindmap_service,
        "parse_structured_response",
        AsyncMock(side_effect=LLMResponseError("boom")),
    )
    service = _service()

    with pytest.raises(MindmapGenerationError, match="boom"):
        await service.generate_and_save(
            user_id=1,
            course_id=2,
            request=GenerateMindmapRequest(week=2, depth=2),
        )


def test_queue_generation_enqueues_celery_task(monkeypatch) -> None:
    service = _service()
    payload = GenerateMindmapRequest(week=2, depth=3)
    delay = Mock(return_value=SimpleNamespace(id="task-123"))
    monkeypatch.setattr(
        "nutrack.mindmaps.tasks.generate_mindmap_task.delay",
        delay,
    )

    response = service.queue_generation(1, 2, payload)

    assert response.task_id == "task-123"
    assert response.status == "queued"
    delay.assert_called_once_with(1, 2, {"week": 2, "depth": 3})


@pytest.mark.asyncio
async def test_get_generation_status_returns_completed_mindmap(monkeypatch) -> None:
    mindmap = SimpleNamespace(
        id=99,
        course_id=2,
        week=3,
        topic="Cells",
        tree_json={"id": "root", "label": "Cells", "description": "", "children": []},
        created_at=datetime.now(timezone.utc),
    )
    service = MindmapService(repo=SimpleNamespace(
        get_by_id_and_user=AsyncMock(return_value=mindmap),
    ))
    monkeypatch.setattr(
        "nutrack.mindmaps.service.AsyncResult",
        lambda task_id, app=None: SimpleNamespace(
            state="SUCCESS",
            result={"mindmap_id": 99},
        ),
    )

    result = await service.get_generation_status(1, 2, "task-123")

    assert result.task_id == "task-123"
    assert result.status == "completed"
    assert result.error_message is None
    assert result.mindmap is not None
    assert result.mindmap.id == 99
    assert result.mindmap.topic == "Cells"


@pytest.mark.asyncio
async def test_get_generation_status_returns_failure_message(monkeypatch) -> None:
    service = _service()
    monkeypatch.setattr(
        "nutrack.mindmaps.service.AsyncResult",
        lambda task_id, app=None: SimpleNamespace(
            state="FAILURE",
            result=RuntimeError("boom"),
        ),
    )

    result = await service.get_generation_status(1, 2, "task-123")

    assert result.task_id == "task-123"
    assert result.status == "failed"
    assert result.error_message == "boom"


@pytest.mark.asyncio
async def test_generate_and_save_skips_invalid_parent_links(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parsed = MindmapLLMResponse(
        root_id="root",
        nodes=[
            MindmapLLMNode(
                id="root",
                label="Topic",
                description="Root description.",
                child_ids=["child"],
            ),
            MindmapLLMNode(
                id="child",
                label="Child",
                description="Child description.",
                parent_id="other",
            ),
        ],
    )
    monkeypatch.setattr(
        mindmap_service,
        "parse_structured_response",
        AsyncMock(return_value=parsed),
    )
    service = _service()

    result = await service.generate_and_save(
        user_id=1,
        course_id=2,
        request=GenerateMindmapRequest(week=2, depth=2),
    )

    assert result.root.label == "Topic"
    assert result.root.children == []


@pytest.mark.asyncio
async def test_generate_and_save_skips_unknown_child_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    parsed = MindmapLLMResponse(
        root_id="root",
        nodes=[
            MindmapLLMNode(
                id="root",
                label="Topic",
                description="Root description.",
                child_ids=["child", "missing"],
            ),
            MindmapLLMNode(
                id="child",
                label="Child",
                description="Child description.",
                parent_id="root",
            ),
        ],
    )
    monkeypatch.setattr(
        mindmap_service,
        "parse_structured_response",
        AsyncMock(return_value=parsed),
    )
    service = _service()

    result = await service.generate_and_save(
        user_id=1,
        course_id=2,
        request=GenerateMindmapRequest(week=2, depth=2),
    )

    assert result.root.label == "Topic"
    assert len(result.root.children) == 1
    assert result.root.children[0].label == "Child"




@pytest.mark.asyncio
async def test_generate_and_save_trims_large_material_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured = {}
    parsed = MindmapLLMResponse(
        root_id="root",
        nodes=[
            MindmapLLMNode(
                id="root",
                label="Large Topic",
                description="Root description.",
                child_ids=[],
            )
        ],
    )

    async def fake_parse(**kwargs):
        captured["user_prompt"] = kwargs["user_prompt"]
        return parsed

    material_repo = SimpleNamespace(
        list_completed_uploads_for_week=AsyncMock(
            return_value=[
                SimpleNamespace(
                    original_filename="week1.pdf",
                    storage_key="material/week1.pdf",
                )
            ]
        ),
    )
    storage = SimpleNamespace(
        download_file_bytes=AsyncMock(return_value=b"%PDF-1.4"),
    )
    monkeypatch.setattr(mindmap_service, "_extract_pdf_text", lambda _: "A" * 30_000)
    monkeypatch.setattr(mindmap_service, "parse_structured_response", fake_parse)
    service = MindmapService(repo=_repo(), material_repo=material_repo, storage=storage)

    await service.generate_and_save(
        user_id=1,
        course_id=2,
        request=GenerateMindmapRequest(week=1, depth=3),
    )

    assert len(captured["user_prompt"]) < 21_000
    assert "[week1.pdf]" in captured["user_prompt"]


def _service() -> MindmapService:
    repo = _repo()
    material_repo = SimpleNamespace(
        list_completed_uploads_for_week=AsyncMock(return_value=[]),
    )
    return MindmapService(repo=repo, material_repo=material_repo, storage=object())


def _repo() -> SimpleNamespace:
    return SimpleNamespace(create=AsyncMock(side_effect=_create_mindmap))


async def _create_mindmap(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(
        id=99,
        course_id=kwargs["course_id"],
        week=kwargs["week"],
        topic=kwargs["topic"],
        tree_json=kwargs["tree_json"],
        created_at=datetime.now(timezone.utc),
    )
