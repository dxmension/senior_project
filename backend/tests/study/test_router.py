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


def _mock_exam_dashboard() -> dict:
    return {
        "id": 4,
        "course_id": 2,
        "course_code": "CSCI 151",
        "course_title": "Programming",
        "assessment_type": "midterm",
        "assessment_number": 1,
        "title": "Midterm 1 Mock 2",
        "version": 2,
        "question_count": 3,
        "time_limit_minutes": 40,
        "instructions": "Choose the best answer.",
        "created_at": "2026-04-15T09:00:00Z",
        "sources": [
            {"source": "historic", "label": "Historic"},
            {"source": "ai", "label": "AI"},
        ],
        "attempts_count": 2,
        "best_score_pct": 88.5,
        "average_score_pct": 79.2,
        "latest_score_pct": 88.5,
        "predicted_score_pct": 84.3,
        "predicted_grade_letter": "B",
        "improvement_pct": 12.0,
        "active_attempt": None,
        "attempts": [
            {
                "id": 11,
                "status": "completed",
                "score_pct": 88.5,
                "started_at": "2026-04-16T09:00:00Z",
                "submitted_at": "2026-04-16T09:30:00Z",
            }
        ],
        "trend": [{"date_label": "Apr 16", "best_score_pct": 88.5}],
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


@pytest.mark.asyncio
async def test_list_mock_exams_returns_groups(
    client,
    current_user,
    test_app,
) -> None:
    payload = [
        {
            "course_id": 2,
            "course_code": "CSCI 151",
            "course_title": "Programming",
            "predicted_score_pct": 86.7,
            "predicted_grade_letter": "B+",
            "assessment_predictions": [
                {
                    "assessment_type": "midterm",
                    "predicted_score_pct": 86.7,
                    "predicted_grade_letter": "B+",
                }
            ],
            "exams": [
                {
                    "id": 4,
                    "assessment_number": 1,
                    "title": "Midterm 1 Mock 1",
                    "assessment_type": "midterm",
                    "version": 1,
                    "question_count": 20,
                    "time_limit_minutes": 40,
                    "created_at": "2026-04-16T09:00:00Z",
                    "sources": [{"source": "historic", "label": "Historic"}],
                    "best_score_pct": 88.5,
                    "average_score_pct": 82.0,
                    "latest_score_pct": 88.5,
                    "predicted_score_pct": 86.7,
                    "predicted_grade_letter": "B+",
                    "attempts_count": 2,
                    "completed_attempts": 2,
                    "has_active_attempt": False,
                }
            ],
        }
    ]
    service = SimpleNamespace(list_mock_exams=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.get("/v1/study/mock-exams")

    assert response.status_code == 200
    assert response.json()["data"][0]["course_code"] == "CSCI 151"
    service.list_mock_exams.assert_awaited_once_with(current_user.id)


@pytest.mark.asyncio
async def test_get_mock_exam_dashboard_returns_stats(
    client,
    current_user,
    test_app,
) -> None:
    service = SimpleNamespace(
        get_mock_exam_dashboard=AsyncMock(return_value=_mock_exam_dashboard())
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.get("/v1/study/mock-exams/4")

    assert response.status_code == 200
    assert response.json()["data"]["title"] == "Midterm 1 Mock 2"
    service.get_mock_exam_dashboard.assert_awaited_once_with(current_user.id, 4)


@pytest.mark.asyncio
async def test_get_mock_exam_attempt_returns_session(
    client,
    current_user,
    test_app,
) -> None:
    payload = {
        "id": 21,
        "mock_exam_id": 4,
        "course_id": 2,
        "course_code": "CSCI 151",
        "course_title": "Programming",
        "assessment_type": "midterm",
        "assessment_number": 1,
        "title": "Midterm 1 Mock 2",
        "status": "in_progress",
        "started_at": "2026-04-16T09:00:00Z",
        "submitted_at": None,
        "last_active_at": "2026-04-16T09:00:00Z",
        "current_position": 1,
        "answered_count": 0,
        "correct_count": 0,
        "score_pct": None,
        "question_count": 2,
        "time_limit_minutes": 40,
        "instructions": "Choose the best answer.",
        "questions": [],
        "answers": [],
    }
    service = SimpleNamespace(get_mock_exam_attempt=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.get("/v1/study/mock-exams/attempts/21")

    assert response.status_code == 200
    assert response.json()["data"]["mock_exam_id"] == 4
    service.get_mock_exam_attempt.assert_awaited_once_with(current_user.id, 21)


@pytest.mark.asyncio
async def test_get_mock_exam_attempt_review_returns_review(
    client,
    current_user,
    test_app,
) -> None:
    payload = {
        "id": 21,
        "mock_exam_id": 4,
        "course_id": 2,
        "course_code": "CSCI 151",
        "course_title": "Programming",
        "assessment_type": "midterm",
        "assessment_number": 1,
        "title": "Midterm 1 Mock 2",
        "status": "completed",
        "started_at": "2026-04-16T09:00:00Z",
        "submitted_at": "2026-04-16T09:30:00Z",
        "last_active_at": "2026-04-16T09:30:00Z",
        "current_position": 2,
        "answered_count": 2,
        "correct_count": 1,
        "score_pct": 50.0,
        "question_count": 2,
        "time_limit_minutes": 40,
        "instructions": "Choose the best answer.",
        "review_questions": [],
    }
    service = SimpleNamespace(
        get_mock_exam_attempt_review=AsyncMock(return_value=payload)
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.get("/v1/study/mock-exams/attempts/21/review")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "completed"
    service.get_mock_exam_attempt_review.assert_awaited_once_with(
        current_user.id,
        21,
    )


@pytest.mark.asyncio
async def test_start_mock_exam_attempt_returns_attempt(
    client,
    current_user,
    test_app,
) -> None:
    payload = {
        "id": 21,
        "status": "in_progress",
        "started_at": "2026-04-16T09:00:00Z",
        "submitted_at": None,
        "last_active_at": "2026-04-16T09:00:00Z",
        "current_position": 1,
        "answered_count": 0,
        "correct_count": 0,
        "score_pct": None,
    }
    service = SimpleNamespace(
        start_mock_exam_attempt=AsyncMock(return_value=payload)
    )
    test_app.dependency_overrides[get_current_user] = lambda: current_user
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.post("/v1/study/mock-exams/4/attempts")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "in_progress"
    service.start_mock_exam_attempt.assert_awaited_once_with(current_user.id, 4)


@pytest.mark.asyncio
async def test_admin_list_mock_exams_returns_items(client, test_app) -> None:
    admin = SimpleNamespace(id=99, is_admin=True, email="admin@nu.edu.kz")
    payload = [
        {
            "id": 4,
            "course_id": 2,
            "course_code": "CSCI 151",
            "course_title": "Programming",
            "assessment_type": "midterm",
            "assessment_number": 1,
            "title": "Midterm 1 Mock 2",
            "version": 2,
            "is_active": True,
            "question_count": 20,
            "time_limit_minutes": 40,
            "instructions": "Choose the best answer.",
            "total_attempts": 12,
            "completed_attempts": 10,
            "average_score_pct": 76.1,
            "best_score_pct": 91.0,
            "active_attempts": 2,
            "created_at": "2026-04-16T09:00:00Z",
            "updated_at": "2026-04-16T09:00:00Z",
        }
    ]
    service = SimpleNamespace(list_admin_mock_exams=AsyncMock(return_value=payload))
    test_app.dependency_overrides[get_current_admin_user] = lambda: admin
    test_app.dependency_overrides[get_study_service] = lambda: service

    response = await client.get("/v1/admin/mock-exams?course_id=2")

    assert response.status_code == 200
    assert response.json()["data"][0]["version"] == 2
    service.list_admin_mock_exams.assert_awaited_once_with(2)
