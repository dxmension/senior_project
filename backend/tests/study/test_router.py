from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from nutrack.auth.dependencies import get_current_admin_user, get_current_user
from nutrack.study.dependencies import get_study_service
from nutrack.study.router import router


def _upload_payload() -> dict:
    return {
        "id": 1,
        "course_id": 7,
        "course_code": "CSCI 151",
        "course_title": "Programming",
        "week": 2,
        "original_filename": "notes.pdf",
        "content_type": "application/pdf",
        "file_size_bytes": 512,
        "upload_status": "queued",
        "curation_status": "pending",
        "publish_requested": True,
        "error_message": None,
        "is_published": False,
        "download_url": None,
        "created_at": "2026-04-12T10:00:00Z",
        "updated_at": "2026-04-12T10:00:00Z",
    }


def test_study_router_keeps_prefix_and_tags() -> None:
    assert router.prefix == "/study"
    assert router.tags == ["study"]


@pytest.mark.asyncio
async def test_list_user_materials_returns_data(
    client,
    current_user,
    test_app,
) -> None:
    service = SimpleNamespace(
        list_user_uploads=AsyncMock(return_value=[_upload_payload()]),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.get("/v1/study/7/materials/uploads")

    assert response.status_code == 200
    assert response.json()["data"][0]["id"] == 1
    service.list_user_uploads.assert_awaited_once_with(current_user.id, 7)


@pytest.mark.asyncio
async def test_upload_materials_queues_batch(
    client,
    current_user,
    test_app,
) -> None:
    service = SimpleNamespace(
        queue_uploads=AsyncMock(
            return_value=[{**_upload_payload(), "id": 11, "week": 4}]
        ),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.post(
        "/v1/study/7/materials/uploads",
        data={"week": "4"},
        files=[("files", ("notes.pdf", b"pdf", "application/pdf"))],
    )

    assert response.status_code == 201
    assert response.json()["data"][0]["id"] == 11
    service.queue_uploads.assert_awaited_once()
    assert service.queue_uploads.await_args.args[:4] == (current_user.id, 7, 4, False)


@pytest.mark.asyncio
async def test_admin_publish_material_upload_returns_entry(
    client,
    test_app,
) -> None:
    admin = SimpleNamespace(id=99, is_admin=True, email="admin@nu.edu.kz")
    service = SimpleNamespace(
        publish_upload=AsyncMock(
            return_value={
                "id": 3,
                "upload_id": 8,
                "course_id": 7,
                "course_code": "CSCI 151",
                "course_title": "Programming",
                "week": 5,
                "title": "Week 5 slides",
                "original_filename": "slides.pdf",
                "content_type": "application/pdf",
                "file_size_bytes": 1024,
                "download_url": "http://example.com/file",
                "is_owned_by_current_user": True,
                "published_at": "2026-04-12T10:00:00Z",
            }
        )
    )
    test_app.dependency_overrides[get_current_admin_user] = lambda: admin
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.post(
        "/v1/admin/materials/uploads/8/publish",
        json={"title": "Week 5 slides", "week": 5},
    )

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Week 5 slides"
    service.publish_upload.assert_awaited_once_with(99, 8, "Week 5 slides", 5)


@pytest.mark.asyncio
async def test_delete_user_material_calls_service(
    client,
    current_user,
    test_app,
) -> None:
    service = SimpleNamespace(
        delete_user_upload=AsyncMock(return_value={"deleted": True}),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.delete("/v1/study/7/materials/uploads/9")

    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True
    service.delete_user_upload.assert_awaited_once_with(current_user.id, 7, 9)


@pytest.mark.asyncio
async def test_cancel_publish_returns_upload_payload(
    client,
    current_user,
    test_app,
) -> None:
    payload = {**_upload_payload(), "publish_requested": False, "curation_status": "not_requested"}
    service = SimpleNamespace(
        cancel_user_publish=AsyncMock(return_value=payload),
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.post("/v1/study/7/materials/uploads/9/cancel-publish")

    assert response.status_code == 200
    assert response.json()["data"]["curation_status"] == "not_requested"
    service.cancel_user_publish.assert_awaited_once_with(current_user.id, 7, 9)


@pytest.mark.asyncio
async def test_admin_unpublish_material_upload_returns_private_upload(
    client,
    test_app,
) -> None:
    admin = SimpleNamespace(id=99, is_admin=True, email="admin@nu.edu.kz")
    payload = {**_upload_payload(), "publish_requested": False, "curation_status": "not_requested"}
    service = SimpleNamespace(
        unpublish_upload=AsyncMock(return_value=payload),
    )
    test_app.dependency_overrides[get_current_admin_user] = lambda: admin
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.post("/v1/admin/materials/uploads/8/unpublish")

    assert response.status_code == 200
    assert response.json()["data"]["publish_requested"] is False
    service.unpublish_upload.assert_awaited_once_with(8)


@pytest.mark.asyncio
async def test_admin_delete_material_upload_returns_deleted(
    client,
    test_app,
) -> None:
    admin = SimpleNamespace(id=99, is_admin=True, email="admin@nu.edu.kz")
    service = SimpleNamespace(
        delete_upload=AsyncMock(return_value={"deleted": True}),
    )
    test_app.dependency_overrides[get_current_admin_user] = lambda: admin
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.delete("/v1/admin/materials/uploads/8")

    assert response.status_code == 200
    assert response.json()["data"]["deleted"] is True
    service.delete_upload.assert_awaited_once_with(8)
