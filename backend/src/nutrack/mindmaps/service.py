from __future__ import annotations

import asyncio
import io
import uuid
from pathlib import Path

import pdfplumber

from nutrack.course_materials.models import CourseMaterialUpload
from nutrack.course_materials.repository import CourseMaterialUploadRepository
from nutrack.mindmaps.exceptions import (
    MindmapGenerationError,
    MindmapNotFoundError,
    MindmapUnavailableError,
)
from nutrack.mindmaps.models import Mindmap
from nutrack.mindmaps.repository import MindmapRepository
from nutrack.mindmaps.schemas import (
    GenerateMindmapRequest,
    MindmapLLMNode,
    MindmapLLMResponse,
    MindmapNode,
    SavedMindmapResponse,
)
from nutrack.storage import ObjectStorage
from nutrack.tools.llm import (
    LLMConfigurationError,
    LLMError,
    parse_structured_response,
)

_SYSTEM_PROMPT_WITH_MATERIAL = """\
You are a mindmap generator. Given study material excerpts, produce a flat
mindmap that can be reconstructed into a tree.
Rules:
- Return one root node referenced by root_id.
- Each node must include id, label, description, parent_id, and child_ids.
- Root node label should concisely summarize the main topic of the materials (2-6 words).
- Each label should stay within 2-6 words.
- Each description should use 5-8 sentences grounded in the material.
- Every child_id must refer to another node id.
- The graph must stay tree-shaped and acyclic.
- Max depth: {depth} levels from root
- Cover key subtopics, definitions, and relationships found in the material.
"""

_SYSTEM_PROMPT_NO_MATERIAL = """\
You are a mindmap generator. Produce a flat mindmap for the given week's
academic study topics.
Rules:
- Return one root node referenced by root_id.
- Each node must include id, label, description, parent_id, and child_ids.
- Root node label should be a concise academic topic title (2-6 words).
- Each label should stay within 2-6 words.
- Each description should use 5-8 sentences with key examples or details.
- Every child_id must refer to another node id.
- The graph must stay tree-shaped and acyclic.
- Max depth: {depth} levels from root
- Cover key subtopics, definitions, and relationships.
"""


class MindmapService:
    def __init__(
        self,
        repo: MindmapRepository,
        material_repo: CourseMaterialUploadRepository | None = None,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.repo = repo
        self.material_repo = material_repo
        self.storage = storage or ObjectStorage()

    async def generate_and_save(
        self,
        user_id: int,
        course_id: int,
        request: GenerateMindmapRequest,
    ) -> SavedMindmapResponse:
        material_text = await _extract_week_material_text(
            self.material_repo,
            self.storage,
            user_id,
            course_id,
            request.week,
        )
        raw = await _generate_mindmap(request.week, request.depth, material_text)
        root = _build_tree(raw, request.depth)
        topic = root.label or f"Week {request.week}"
        mindmap = await self.repo.create(
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            topic=topic,
            tree_json=root.model_dump(),
        )
        return _to_response(mindmap)

    async def list_for_course(
        self, user_id: int, course_id: int
    ) -> list[SavedMindmapResponse]:
        mindmaps = await self.repo.list_by_course_and_user(user_id, course_id)
        return [_to_response(m) for m in mindmaps]

    async def delete(
        self, user_id: int, course_id: int, mindmap_id: int
    ) -> None:
        mindmap = await self.repo.get_by_id_and_user(mindmap_id, user_id)
        if not mindmap or mindmap.course_id != course_id:
            raise MindmapNotFoundError()
        await self.repo.delete(mindmap)


def _extract_pdf_text(data: bytes) -> str:
    text_parts: list[str] = []
    with pdfplumber.open(io.BytesIO(data)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text:
                text_parts.append(page_text.strip())
    return "\n".join(text_parts)


def _to_response(mindmap: Mindmap) -> SavedMindmapResponse:
    root = MindmapNode.model_validate(mindmap.tree_json)
    return SavedMindmapResponse(
        id=mindmap.id,
        course_id=mindmap.course_id,
        week=mindmap.week,
        topic=mindmap.topic,
        root=root,
        created_at=mindmap.created_at,
    )


async def _extract_week_material_text(
    material_repo: CourseMaterialUploadRepository | None,
    storage: ObjectStorage,
    user_id: int,
    course_id: int,
    week: int,
) -> str:
    if material_repo is None:
        return ""
    uploads = await material_repo.list_completed_uploads_for_week(
        user_id, course_id, week
    )
    parts = await _material_parts(storage, uploads)
    return "\n\n".join(parts)


async def _material_parts(
    storage: ObjectStorage,
    uploads: list[CourseMaterialUpload],
) -> list[str]:
    parts: list[str] = []
    for upload in uploads:
        text = await _extract_text(storage, upload)
        if text:
            parts.append(f"[{upload.original_filename}]\n{text}")
    return parts


async def _extract_text(storage: ObjectStorage, upload: CourseMaterialUpload) -> str:
    suffix = Path(upload.original_filename).suffix.lower()
    if suffix != ".pdf":
        return ""
    try:
        data = await storage.download_file_bytes(upload.storage_key)
        return await asyncio.to_thread(_extract_pdf_text, data)
    except Exception:
        return ""


async def _generate_mindmap(
    week: int,
    depth: int,
    material_text: str,
) -> MindmapLLMResponse:
    system_prompt, user_prompt = _mindmap_prompts(week, depth, material_text)
    try:
        return await parse_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MindmapLLMResponse,
        )
    except LLMConfigurationError as exc:
        raise MindmapUnavailableError() from exc
    except LLMError as exc:
        raise MindmapGenerationError(str(exc)) from exc


def _mindmap_prompts(week: int, depth: int, material_text: str) -> tuple[str, str]:
    if material_text:
        system_prompt = _SYSTEM_PROMPT_WITH_MATERIAL.format(depth=depth)
        user_prompt = (
            f"Study material from Week {week}:\n{material_text}\n\n"
            "Generate a mindmap grounded in these materials."
        )
        return system_prompt, user_prompt
    system_prompt = _SYSTEM_PROMPT_NO_MATERIAL.format(depth=depth)
    user_prompt = f"Generate a mindmap for Week {week} study topics."
    return system_prompt, user_prompt


def _build_tree(raw: MindmapLLMResponse, depth_remaining: int) -> MindmapNode:
    nodes = _node_index(raw.nodes)
    _validate_root(raw.root_id, nodes)
    try:
        return _build_node(raw.root_id, nodes, depth_remaining, set())
    except ValueError as exc:
        raise MindmapGenerationError(str(exc)) from exc


def _node_index(nodes: list[MindmapLLMNode]) -> dict[str, MindmapLLMNode]:
    indexed: dict[str, MindmapLLMNode] = {}
    for node in nodes:
        if node.id in indexed:
            raise MindmapGenerationError(f"Duplicate node id: {node.id}")
        indexed[node.id] = node
    return indexed


def _validate_root(root_id: str, nodes: dict[str, MindmapLLMNode]) -> None:
    root = nodes.get(root_id)
    if root is None:
        raise MindmapGenerationError(f"Unknown root node: {root_id}")
    if root.parent_id is not None:
        raise MindmapGenerationError("Root node must not have a parent_id")


def _build_node(
    node_id: str,
    nodes: dict[str, MindmapLLMNode],
    depth_remaining: int,
    path: set[str],
) -> MindmapNode:
    if node_id in path:
        raise ValueError(f"Cycle detected at node: {node_id}")
    node = _require_node(node_id, nodes)
    next_path = path | {node_id}
    children = _build_children(node, nodes, depth_remaining, next_path)
    return MindmapNode(
        id=uuid.uuid4().hex[:12],
        label=node.label,
        description=node.description,
        children=children,
    )


def _build_children(
    node: MindmapLLMNode,
    nodes: dict[str, MindmapLLMNode],
    depth_remaining: int,
    path: set[str],
) -> list[MindmapNode]:
    if depth_remaining <= 1:
        return []
    return [
        _build_child(child_id, node.id, nodes, depth_remaining - 1, path)
        for child_id in node.child_ids
    ]


def _build_child(
    child_id: str,
    parent_id: str,
    nodes: dict[str, MindmapLLMNode],
    depth_remaining: int,
    path: set[str],
) -> MindmapNode:
    child = _require_node(child_id, nodes)
    if child.parent_id != parent_id:
        raise ValueError(f"Invalid parent for node: {child.id}")
    return _build_node(child_id, nodes, depth_remaining, path)


def _require_node(node_id: str, nodes: dict[str, MindmapLLMNode]) -> MindmapLLMNode:
    node = nodes.get(node_id)
    if node is None:
        raise ValueError(f"Unknown node id: {node_id}")
    return node
