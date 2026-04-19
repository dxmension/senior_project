from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.mindmaps.exceptions import (
    MindmapGenerationError,
    MindmapUnavailableError,
)
from nutrack.mindmaps.schemas import (
    GenerateMindmapRequest,
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


@pytest.mark.asyncio
async def test_generate_and_save_rejects_invalid_parent_links(
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

    with pytest.raises(MindmapGenerationError, match="Invalid parent"):
        await service.generate_and_save(
            user_id=1,
            course_id=2,
            request=GenerateMindmapRequest(week=2, depth=2),
        )


def _service() -> MindmapService:
    repo = SimpleNamespace(create=AsyncMock(side_effect=_create_mindmap))
    material_repo = SimpleNamespace(
        list_completed_uploads_for_week=AsyncMock(return_value=[]),
    )
    return MindmapService(repo=repo, material_repo=material_repo, storage=object())


async def _create_mindmap(**kwargs: object) -> SimpleNamespace:
    return SimpleNamespace(
        id=99,
        course_id=kwargs["course_id"],
        week=kwargs["week"],
        topic=kwargs["topic"],
        tree_json=kwargs["tree_json"],
        created_at=datetime.now(timezone.utc),
    )
