from __future__ import annotations

import asyncio
import io
import uuid
from pathlib import Path

import pdfplumber
from celery.result import AsyncResult

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
    MindmapGenerationQueuedResponse,
    MindmapGenerationStatusResponse,
    MindmapLLMNode,
    MindmapLLMResponse,
    MindmapNode,
    SavedMindmapResponse,
)
from nutrack.logging import get_logger, log_step
from nutrack.storage import ObjectStorage
from nutrack.tools.llm import (
    LLMConfigurationError,
    LLMError,
    parse_structured_response,
)

MAX_SOURCE_TEXT_CHARS = 20_000
MAX_FILE_TEXT_CHARS = 8_000
logger = get_logger(__name__)

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
        log_step(
            logger,
            "mindmap_generation_started",
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            depth=request.depth,
        )
        material_text = await _extract_week_material_text(
            self.material_repo,
            self.storage,
            user_id,
            course_id,
            request.week,
        )
        log_step(
            logger,
            "mindmap_material_text_ready",
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            chars=len(material_text),
        )
        raw = await _generate_mindmap(request.week, request.depth, material_text)
        log_step(
            logger,
            "mindmap_llm_response_ready",
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            node_count=len(raw.nodes),
        )
        root = _build_tree_with_logs(raw, request, user_id, course_id)
        topic = root.label or f"Week {request.week}"
        mindmap = await _save_mindmap(
            self.repo,
            user_id,
            course_id,
            request.week,
            topic,
            root.model_dump(),
        )
        log_step(
            logger,
            "mindmap_saved",
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            mindmap_id=mindmap.id,
            topic=topic,
        )
        return _to_response(mindmap)

    async def list_for_course(
        self, user_id: int, course_id: int
    ) -> list[SavedMindmapResponse]:
        mindmaps = await self.repo.list_by_course_and_user(user_id, course_id)
        return [_to_response(m) for m in mindmaps]

    def queue_generation(
        self,
        user_id: int,
        course_id: int,
        request: GenerateMindmapRequest,
    ) -> MindmapGenerationQueuedResponse:
        from nutrack.mindmaps.tasks import generate_mindmap_task

        task = generate_mindmap_task.delay(user_id, course_id, request.model_dump())
        return MindmapGenerationQueuedResponse(task_id=str(task.id), status="queued")

    async def get_generation_status(
        self,
        user_id: int,
        course_id: int,
        task_id: str,
    ) -> MindmapGenerationStatusResponse:
        from nutrack.celery_app import celery_app

        task = AsyncResult(task_id, app=celery_app)
        status = _task_status(task.state)
        if status == "completed":
            return await _completed_status(self.repo, user_id, course_id, task_id, task.result)
        if status == "failed":
            return MindmapGenerationStatusResponse(
                task_id=task_id,
                status=status,
                error_message=str(task.result),
            )
        return MindmapGenerationStatusResponse(task_id=task_id, status=status)

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
    log_step(
        logger,
        "mindmap_materials_loaded",
        user_id=user_id,
        course_id=course_id,
        week=week,
        upload_count=len(uploads),
    )
    parts = await _material_parts(storage, uploads)
    return _trim_material_text("\n\n".join(parts))


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
        log_step(
            logger,
            "mindmap_material_skipped",
            filename=upload.original_filename,
            reason="unsupported_extension",
        )
        return ""
    try:
        data = await storage.download_file_bytes(upload.storage_key)
        text = await asyncio.to_thread(_extract_pdf_text, data)
        trimmed = _trim_file_text(text)
        log_step(
            logger,
            "mindmap_material_extracted",
            filename=upload.original_filename,
            chars=len(trimmed),
        )
        return trimmed
    except Exception as exc:
        log_step(
            logger,
            "mindmap_material_extract_failed",
            filename=upload.original_filename,
            error=str(exc),
        )
        return ""


async def _generate_mindmap(
    week: int,
    depth: int,
    material_text: str,
) -> MindmapLLMResponse:
    system_prompt, user_prompt = _mindmap_prompts(week, depth, material_text)
    log_step(
        logger,
        "mindmap_llm_request_started",
        week=week,
        depth=depth,
        has_material=bool(material_text),
        material_chars=len(material_text),
        prompt_chars=len(system_prompt) + len(user_prompt),
    )
    try:
        response = await parse_structured_response(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            response_model=MindmapLLMResponse,
            max_output_tokens=2_500,
        )
        log_step(
            logger,
            "mindmap_llm_request_completed",
            week=week,
            depth=depth,
            node_count=len(response.nodes),
        )
        return response
    except LLMConfigurationError as exc:
        log_step(logger, "mindmap_llm_unavailable", week=week, error=str(exc))
        raise MindmapUnavailableError() from exc
    except LLMError as exc:
        log_step(logger, "mindmap_llm_failed", week=week, error=str(exc))
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


def _trim_file_text(text: str) -> str:
    return text[:MAX_FILE_TEXT_CHARS].strip()


def _trim_material_text(text: str) -> str:
    return text[:MAX_SOURCE_TEXT_CHARS].strip()


def _task_status(state: str) -> str:
    mapped = {
        "PENDING": "queued",
        "RECEIVED": "queued",
        "STARTED": "processing",
        "RETRY": "processing",
        "SUCCESS": "completed",
        "FAILURE": "failed",
    }
    return mapped.get(state, "processing")


async def _completed_status(
    repo: MindmapRepository,
    user_id: int,
    course_id: int,
    task_id: str,
    result: object,
) -> MindmapGenerationStatusResponse:
    mindmap_id = _mindmap_id_from_result(result)
    if mindmap_id is None:
        return MindmapGenerationStatusResponse(
            task_id=task_id,
            status="failed",
            error_message="Mindmap task completed without a result id",
        )
    mindmap = await repo.get_by_id_and_user(mindmap_id, user_id)
    if mindmap is None or mindmap.course_id != course_id:
        return MindmapGenerationStatusResponse(
            task_id=task_id,
            status="failed",
            error_message="Generated mindmap could not be loaded",
        )
    return MindmapGenerationStatusResponse(
        task_id=task_id,
        status="completed",
        mindmap=_to_response(mindmap),
    )


def _mindmap_id_from_result(result: object) -> int | None:
    if not isinstance(result, dict):
        return None
    value = result.get("mindmap_id")
    return value if isinstance(value, int) else None


def _build_tree_with_logs(
    raw: MindmapLLMResponse,
    request: GenerateMindmapRequest,
    user_id: int,
    course_id: int,
) -> MindmapNode:
    log_step(
        logger,
        "mindmap_tree_build_started",
        user_id=user_id,
        course_id=course_id,
        week=request.week,
        depth=request.depth,
    )
    try:
        root = _build_tree(raw, request.depth)
    except MindmapGenerationError as exc:
        log_step(
            logger,
            "mindmap_tree_build_failed",
            user_id=user_id,
            course_id=course_id,
            week=request.week,
            error=str(exc),
        )
        raise
    log_step(
        logger,
        "mindmap_tree_build_completed",
        user_id=user_id,
        course_id=course_id,
        week=request.week,
        root_label=root.label,
        child_count=len(root.children),
    )
    return root


async def _save_mindmap(
    repo: MindmapRepository,
    user_id: int,
    course_id: int,
    week: int,
    topic: str,
    tree_json: dict,
) -> Mindmap:
    log_step(
        logger,
        "mindmap_save_started",
        user_id=user_id,
        course_id=course_id,
        week=week,
        topic=topic,
    )
    try:
        return await repo.create(
            user_id=user_id,
            course_id=course_id,
            week=week,
            topic=topic,
            tree_json=tree_json,
        )
    except Exception as exc:
        log_step(
            logger,
            "mindmap_save_failed",
            user_id=user_id,
            course_id=course_id,
            week=week,
            error=str(exc),
        )
        raise


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
    children: list[MindmapNode] = []
    for child_id in node.child_ids:
        child = nodes.get(child_id)
        if child is None:
            log_step(
                logger,
                "mindmap_tree_child_skipped",
                parent_id=node.id,
                child_id=child_id,
                reason="unknown_node",
            )
            continue
        if child.parent_id != node.id:
            log_step(
                logger,
                "mindmap_tree_child_skipped",
                parent_id=node.id,
                child_id=child.id,
                reason="invalid_parent",
                child_parent_id=child.parent_id,
            )
            continue
        children.append(
            _build_child(child.id, node.id, nodes, depth_remaining - 1, path)
        )
    return children


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
