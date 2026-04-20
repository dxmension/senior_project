from datetime import datetime, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import UploadFile

from nutrack.assessments.models import AssessmentType
from nutrack.course_materials.models import (
    MaterialCurationStatus,
    MaterialUploadStatus,
)
from nutrack.course_materials.service import CourseMaterialService
from nutrack.mock_exams.models import (
    MockExamAttemptStatus,
    MockExamOrigin,
    MockExamQuestionSource,
    MockExamVisibilityScope,
)
from nutrack.mock_exams.service import MockExamService


def _upload_file(
    name: str = "notes.pdf",
    content_type: str = "application/pdf",
) -> UploadFile:
    return UploadFile(filename=name, file=BytesIO(b"payload"), headers={"content-type": content_type})


@pytest.mark.asyncio
async def test_queue_uploads_commits_and_enqueues(monkeypatch) -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    offering = SimpleNamespace(
        id=7,
        course=SimpleNamespace(title="Intro to Programming"),
    )
    upload = SimpleNamespace(id=11)
    service.upload_repo = SimpleNamespace(
        get_enrolled_course=AsyncMock(return_value=offering),
        get_upload_by_id=AsyncMock(return_value=upload),
    )
    service._create_upload = AsyncMock(return_value=upload)
    service._cleanup_stale_uploads = AsyncMock()
    service._enqueue_uploads = Mock()
    service._serialize_uploads = AsyncMock(return_value=[{"id": 11}])

    result = await service.queue_uploads(1, 7, 4, False, [_upload_file()])

    assert result == [{"id": 11}]
    session.commit.assert_awaited_once()
    service._enqueue_uploads.assert_called_once_with([upload])


@pytest.mark.asyncio
async def test_publish_upload_creates_library_entry() -> None:
    session = AsyncMock()
    storage = AsyncMock()
    storage.generate_download_url = AsyncMock(return_value="http://example.com/file")
    service = CourseMaterialService(session=session, storage=storage)
    upload = SimpleNamespace(
        id=8,
        course_id=7,
        uploader_id=1,
        storage_key="course/week_5/file.pdf",
        upload_status=MaterialUploadStatus.COMPLETED,
        curation_status=MaterialCurationStatus.PENDING,
    )
    entry = SimpleNamespace(
        id=3,
        upload=SimpleNamespace(
            id=8,
            uploader_id=1,
            storage_key="course/week_5/file.pdf",
            original_filename="file.pdf",
            content_type="application/pdf",
            file_size_bytes=1024,
            course_offering=SimpleNamespace(
                course=SimpleNamespace(code="CSCI", level="151", title="Programming")
            ),
        ),
        course_id=7,
        curated_week=5,
        curated_title="Week 5 slides",
        updated_at="2026-04-12T10:00:00Z",
    )
    service._load_upload = AsyncMock(return_value=upload)
    service._cleanup_stale_uploads = AsyncMock()
    service.library_repo = SimpleNamespace(
        get_by_upload_id=AsyncMock(side_effect=[None, entry]),
        create=AsyncMock(return_value=entry),
        update=AsyncMock(),
    )
    service.upload_repo = SimpleNamespace(update=AsyncMock())

    result = await service.publish_upload(99, 8, "Week 5 slides", 5)

    assert result["title"] == "Week 5 slides"
    assert result["download_url"] == "http://example.com/file"
    service.library_repo.create.assert_awaited_once()
    service.upload_repo.update.assert_awaited_once_with(
        upload,
        curation_status=MaterialCurationStatus.PUBLISHED,
    )


@pytest.mark.asyncio
async def test_list_admin_uploads_hides_private_and_rejected_items() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(
        storage_key="course/week_5/file.pdf",
        course_offering=SimpleNamespace(
            course=SimpleNamespace(code="CSCI", level="151", title="Programming")
        ),
        uploader=SimpleNamespace(
            id=7,
            first_name="Ada",
            last_name="Lovelace",
            email="ada@example.com",
        ),
        library_entry=None,
        id=8,
        course_id=7,
        user_week=5,
        original_filename="file.pdf",
        content_type="application/pdf",
        file_size_bytes=1024,
        upload_status=MaterialUploadStatus.COMPLETED,
        curation_status=MaterialCurationStatus.PENDING,
        error_message=None,
        created_at="2026-04-12T10:00:00Z",
        updated_at="2026-04-12T10:00:00Z",
    )
    service._cleanup_stale_uploads = AsyncMock()
    service._download_url = AsyncMock(return_value="http://example.com/file")
    service.upload_repo = SimpleNamespace(
        list_admin_uploads=AsyncMock(return_value=[upload]),
    )

    result = await service.list_admin_uploads()

    assert result[0]["curation_status"] == "pending"
    service.upload_repo.list_admin_uploads.assert_awaited_once_with(
        course_id=None,
        user_id=None,
        upload_status=None,
        curation_statuses=(
            MaterialCurationStatus.PENDING,
            MaterialCurationStatus.PUBLISHED,
        ),
    )


@pytest.mark.asyncio
async def test_list_admin_uploads_ignores_private_filter() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    service._cleanup_stale_uploads = AsyncMock()
    service.upload_repo = SimpleNamespace(list_admin_uploads=AsyncMock())

    result = await service.list_admin_uploads(
        curation_status=MaterialCurationStatus.NOT_REQUESTED,
    )

    assert result == []
    service.upload_repo.list_admin_uploads.assert_not_called()


@pytest.mark.asyncio
async def test_mark_upload_failed_clears_staged_path() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(staged_path="/tmp/upload", id=9)
    service.upload_repo = SimpleNamespace(
        get_upload_by_id=AsyncMock(return_value=upload),
        update=AsyncMock(),
    )
    service._remove_staged_file = AsyncMock()

    await service.mark_upload_failed(9, "boom")

    service.upload_repo.update.assert_awaited_once_with(
        upload,
        upload_status=MaterialUploadStatus.FAILED,
        staged_path=None,
        error_message="boom",
    )
    service._remove_staged_file.assert_awaited_once_with("/tmp/upload")


@pytest.mark.asyncio
async def test_create_upload_sets_private_curation_status() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    offering = SimpleNamespace(id=7, course=SimpleNamespace(title="Programming"))
    service._stage_file = AsyncMock(return_value="/tmp/upload")
    service.upload_repo = SimpleNamespace(create=AsyncMock(return_value=SimpleNamespace()))

    await service._create_upload(1, offering, 3, False, _upload_file())  # noqa: SLF001

    assert service.upload_repo.create.await_args.kwargs["curation_status"] == (
        MaterialCurationStatus.NOT_REQUESTED
    )


@pytest.mark.asyncio
async def test_delete_upload_removes_library_entry_and_files() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(
        id=8,
        staged_path="/tmp/upload",
        storage_key="course/file.pdf",
        library_entry=SimpleNamespace(id=2),
    )
    service.upload_repo = SimpleNamespace(delete=AsyncMock())
    service.library_repo = SimpleNamespace(delete=AsyncMock())
    service._remove_staged_file = AsyncMock()
    service._delete_storage_file = AsyncMock()

    result = await service._delete_upload(upload)  # noqa: SLF001

    assert result == {"deleted": True}
    service.library_repo.delete.assert_awaited_once_with(upload.library_entry)
    service.upload_repo.delete.assert_awaited_once_with(upload)
    service._remove_staged_file.assert_awaited_once_with("/tmp/upload")
    service._delete_storage_file.assert_awaited_once_with("course/file.pdf")


@pytest.mark.asyncio
async def test_make_upload_private_deletes_library_entry() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    upload = SimpleNamespace(
        id=8,
        storage_key="course/file.pdf",
        upload_status=MaterialUploadStatus.COMPLETED,
        library_entry=SimpleNamespace(id=5),
    )
    loaded = SimpleNamespace(
        id=8,
        course_id=7,
        uploader_id=1,
        user_week=2,
        original_filename="file.pdf",
        content_type="application/pdf",
        file_size_bytes=10,
        upload_status=MaterialUploadStatus.COMPLETED,
        curation_status=MaterialCurationStatus.NOT_REQUESTED,
        error_message=None,
        library_entry=None,
        storage_key="course/file.pdf",
        created_at="2026-04-12T10:00:00Z",
        updated_at="2026-04-12T10:00:00Z",
        course_offering=SimpleNamespace(
            course=SimpleNamespace(code="CSCI", level="151", title="Programming")
        ),
    )
    service.upload_repo = SimpleNamespace(
        update=AsyncMock(),
        get_upload_by_id=AsyncMock(return_value=loaded),
    )
    service.library_repo = SimpleNamespace(delete=AsyncMock())
    service._download_url = AsyncMock(return_value="http://example.com/file")

    result = await service._make_upload_private(upload)  # noqa: SLF001

    assert result["publish_requested"] is False
    service.upload_repo.update.assert_awaited_once_with(
        upload,
        curation_status=MaterialCurationStatus.NOT_REQUESTED,
    )


@pytest.mark.asyncio
async def test_cleanup_stale_uploads_marks_old_items_failed() -> None:
    session = AsyncMock()
    service = CourseMaterialService(session=session, storage=AsyncMock())
    stale = SimpleNamespace(
        staged_path="/tmp/upload",
        storage_key="course/file.pdf",
    )
    cutoff_check = {}

    async def list_stale_uploads(cutoff, statuses):
        cutoff_check["cutoff"] = cutoff
        cutoff_check["statuses"] = statuses
        return [stale]

    service.upload_repo = SimpleNamespace(
        list_stale_uploads=AsyncMock(side_effect=list_stale_uploads),
        update=AsyncMock(),
    )
    service._remove_staged_file = AsyncMock()
    service._delete_storage_file = AsyncMock()

    await service._cleanup_stale_uploads()  # noqa: SLF001

    assert cutoff_check["cutoff"] < datetime.now(timezone.utc)
    assert MaterialUploadStatus.QUEUED in cutoff_check["statuses"]
    service.upload_repo.update.assert_awaited_once_with(
        stale,
        upload_status=MaterialUploadStatus.FAILED,
        staged_path=None,
        error_message="Upload timed out before completion",
    )


@pytest.mark.asyncio
async def test_list_mock_exams_returns_available_course_exams_by_type() -> None:
    session = AsyncMock()
    service = MockExamService(session=session)
    assessment = SimpleNamespace(
        id=3,
        course_id=7,
        title="Midterm 1",
        assessment_number=1,
        assessment_type=SimpleNamespace(value="midterm"),
        deadline=datetime(2026, 4, 20, tzinfo=timezone.utc),
        course_offering=SimpleNamespace(
            course=SimpleNamespace(id=2, code="CSCI", level="151", title="Programming")
        ),
    )
    latest_exam = SimpleNamespace(
        id=4,
        course_id=2,
        assessment_number=1,
        assessment_type=SimpleNamespace(value="midterm"),
        title="Midterm 1 Mock 2",
        version=2,
        question_count=25,
        time_limit_minutes=40,
        created_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
        course=SimpleNamespace(id=2, code="CSCI", level="151", title="Programming"),
        question_links=[
            SimpleNamespace(
                position=1,
                question=SimpleNamespace(source=MockExamQuestionSource.HISTORIC),
            )
        ],
    )
    older_exam = SimpleNamespace(
        id=3,
        course_id=2,
        assessment_number=1,
        assessment_type=SimpleNamespace(value="midterm"),
        title="Midterm 1 Mock 1",
        version=1,
        question_count=20,
        time_limit_minutes=35,
        created_at=datetime(2026, 4, 12, tzinfo=timezone.utc),
        course=SimpleNamespace(id=2, code="CSCI", level="151", title="Programming"),
        question_links=[
            SimpleNamespace(
                position=1,
                question=SimpleNamespace(source=MockExamQuestionSource.AI),
            )
        ],
    )
    service.assessment_repo = SimpleNamespace(
        get_by_user=AsyncMock(return_value=[assessment]),
    )
    service.enrollment_repo = SimpleNamespace(
        list_by_user=AsyncMock(
            return_value=[
                SimpleNamespace(
                    course_offering=SimpleNamespace(
                        course=SimpleNamespace(
                            id=2,
                            code="CSCI",
                            level="151",
                            title="Programming",
                        )
                    )
                )
            ]
        )
    )
    service.mock_exam_repo = SimpleNamespace(
        list_matching_for_user=AsyncMock(return_value=[latest_exam, older_exam]),
    )
    service.mock_exam_attempt_repo = SimpleNamespace(
        list_active_for_user_exams=AsyncMock(
            return_value=[
                SimpleNamespace(
                    id=22,
                    mock_exam_id=4,
                    status=MockExamAttemptStatus.IN_PROGRESS,
                    started_at=datetime.now(timezone.utc),
                    submitted_at=None,
                    last_active_at=datetime.now(timezone.utc),
                    current_position=2,
                    answered_count=1,
                    correct_count=1,
                    score_pct=None,
                )
            ]
        ),
        get_attempt_stats=AsyncMock(
            return_value={
                4: {
                    "attempts_count": 3,
                    "best_score_pct": 88.5,
                    "average_score_pct": 82.0,
                    "latest_score_pct": 88.5,
                    "predicted_score_pct": 86.7,
                    "completed_attempts": 2,
                    "has_active_attempt": True,
                },
                3: {
                    "attempts_count": 1,
                    "best_score_pct": 70.0,
                    "average_score_pct": 70.0,
                    "latest_score_pct": 70.0,
                    "predicted_score_pct": 72.0,
                    "completed_attempts": 1,
                    "has_active_attempt": False,
                }
            }
        ),
        list_for_user_exams=AsyncMock(
            return_value=[
                SimpleNamespace(
                    mock_exam_id=4,
                    score_pct=88.5,
                    started_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
                    submitted_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
                ),
                SimpleNamespace(
                    mock_exam_id=3,
                    score_pct=70.0,
                    started_at=datetime(2026, 4, 12, tzinfo=timezone.utc),
                    submitted_at=datetime(2026, 4, 12, tzinfo=timezone.utc),
                ),
                SimpleNamespace(
                    mock_exam_id=4,
                    score_pct=85.0,
                    started_at=datetime(2026, 4, 14, tzinfo=timezone.utc),
                    submitted_at=datetime(2026, 4, 14, tzinfo=timezone.utc),
                ),
            ]
        ),
    )

    result = await service.list_mock_exams(1)

    assert result[0]["course_code"] == "CSCI 151"
    assert result[0]["predicted_score_pct"] == 81.2
    assert result[0]["predicted_grade_letter"] == "B"
    assert result[0]["assessment_predictions"][0]["predicted_score_pct"] == 81.2
    assert result[0]["assessment_predictions"][0]["predicted_grade_letter"] == "B"
    assert len(result[0]["exams"]) == 2
    assert result[0]["exams"][0]["id"] == 4
    assert result[0]["exams"][0]["has_active_attempt"] is True
    assert result[0]["exams"][0]["active_attempt"]["id"] == 22
    assert result[0]["exams"][0]["predicted_score_pct"] == 86.7
    assert result[0]["exams"][0]["predicted_grade_letter"] == "B+"
    assert result[0]["exams"][0]["title"] == "Midterm 1 Mock 2"
    assert result[0]["exams"][0]["sources"][0]["label"] == "Historic"
    assert result[0]["exams"][1]["id"] == 3
    assert result[0]["exams"][1]["title"] == "Midterm 1 Mock 1"


def test_dashboard_payload_builds_best_and_trend() -> None:
    service = MockExamService(session=AsyncMock())
    exam = SimpleNamespace(
        id=4,
        course_id=2,
        course=SimpleNamespace(code="CSCI", level="151", title="Programming"),
        assessment_type=SimpleNamespace(value="midterm"),
        title="Midterm 1 Mock 2",
        version=2,
        question_count=3,
        time_limit_minutes=40,
        instructions="Choose the best answer.",
        created_at=datetime(2026, 4, 15, tzinfo=timezone.utc),
        question_links=[
            SimpleNamespace(
                position=1,
                question=SimpleNamespace(source=MockExamQuestionSource.AI),
            )
        ],
    )
    attempts = [
        SimpleNamespace(
            id=3,
            status=MockExamAttemptStatus.IN_PROGRESS,
            score_pct=None,
            started_at=datetime.now(timezone.utc),
            submitted_at=None,
            last_active_at=datetime.now(timezone.utc),
            current_position=2,
            answered_count=1,
            correct_count=1,
        ),
        SimpleNamespace(
            id=2,
            status=SimpleNamespace(value="completed"),
            score_pct=88.0,
            started_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
        ),
        SimpleNamespace(
            id=1,
            status=SimpleNamespace(value="completed"),
            score_pct=70.0,
            started_at=datetime(2026, 4, 14, tzinfo=timezone.utc),
            submitted_at=datetime(2026, 4, 14, tzinfo=timezone.utc),
        ),
    ]

    payload = service._dashboard_payload(exam, attempts)  # noqa: SLF001

    assert payload["best_score_pct"] == 88.0
    assert payload["attempts_count"] == 3
    assert payload["predicted_score_pct"] == 79.0
    assert payload["predicted_grade_letter"] == "B-"
    assert payload["improvement_pct"] == 18.0
    assert payload["trend"][-1]["best_score_pct"] == 88.0
    assert payload["sources"][0]["label"] == "AI"
    assert payload["active_attempt"]["status"] == "in_progress"
    assert payload["active_attempt"]["expires_at"] is not None
    assert "questions" not in payload


def test_attempt_review_payload_includes_correctness() -> None:
    service = MockExamService(session=AsyncMock())
    question = SimpleNamespace(
        id=5,
        course_id=2,
        source=MockExamQuestionSource.HISTORIC,
        historical_course_offering_id=None,
        question_text="What is Python?",
        answer_variant_1="A language",
        answer_variant_2="A database",
        answer_variant_3=None,
        answer_variant_4=None,
        answer_variant_5=None,
        answer_variant_6=None,
        correct_option_index=1,
        explanation="It is a language.",
    )
    link = SimpleNamespace(id=9, position=1, points=2, question=question)
    exam = SimpleNamespace(
        id=4,
        course_id=2,
        course=SimpleNamespace(code="CSCI", level="151", title="Programming"),
        assessment_type=SimpleNamespace(value="midterm"),
        title="Midterm 1 Mock 2",
        question_count=1,
        time_limit_minutes=40,
        instructions="Choose the best answer.",
        question_links=[link],
    )
    attempt = SimpleNamespace(
        id=21,
        mock_exam_id=4,
        status=SimpleNamespace(value="completed"),
        started_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
        submitted_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
        last_active_at=datetime(2026, 4, 16, tzinfo=timezone.utc),
        current_position=1,
        answered_count=1,
        correct_count=0,
        score_pct=0.0,
        mock_exam=exam,
        answers=[
            SimpleNamespace(
                mock_exam_question_link_id=9,
                selected_option_index=2,
                is_correct=False,
            )
        ],
    )

    payload = service._attempt_review_payload(attempt)  # noqa: SLF001

    assert payload["review_questions"][0]["selected_option_index"] == 2
    assert payload["review_questions"][0]["question"]["correct_option_index"] == 1


@pytest.mark.asyncio
async def test_sync_attempt_timeout_auto_submits_expired_attempt() -> None:
    session = AsyncMock()
    service = MockExamService(session=session)
    question = SimpleNamespace(correct_option_index=1)
    exam = SimpleNamespace(
        id=4,
        time_limit_minutes=30,
        question_links=[
            SimpleNamespace(id=9, position=1, question=question),
            SimpleNamespace(id=10, position=2, question=question),
        ],
    )
    expired_attempt = SimpleNamespace(
        id=21,
        status=MockExamAttemptStatus.IN_PROGRESS,
        started_at=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc),
        submitted_at=None,
        last_active_at=datetime(2026, 4, 16, 9, 5, tzinfo=timezone.utc),
        answers=[
            SimpleNamespace(
                mock_exam_question_link_id=9,
                selected_option_index=1,
                is_correct=True,
            ),
            SimpleNamespace(
                mock_exam_question_link_id=10,
                selected_option_index=None,
                is_correct=None,
            ),
        ],
    )

    async def update_attempt(entity, **data):
        for key, value in data.items():
            setattr(entity, key, value)
        return entity

    service.mock_exam_attempt_repo = SimpleNamespace(
        get_by_id=AsyncMock(return_value=expired_attempt),
        update=AsyncMock(side_effect=update_attempt),
    )

    expired = await service._sync_attempt_timeout(expired_attempt, exam)  # noqa: SLF001

    assert expired is True
    assert expired_attempt.status == MockExamAttemptStatus.COMPLETED
    assert expired_attempt.submitted_at == datetime(
        2026,
        4,
        16,
        9,
        30,
        tzinfo=timezone.utc,
    )
    assert expired_attempt.score_pct == 50.0


@pytest.mark.asyncio
async def test_submit_mock_exam_attempt_returns_completed_payload() -> None:
    session = AsyncMock()
    service = MockExamService(session=session)
    exam = SimpleNamespace(
        id=4,
        mock_exam_id=4,
        time_limit_minutes=40,
        question_links=[SimpleNamespace(id=9, position=1)],
    )
    attempt = SimpleNamespace(
        id=21,
        mock_exam_id=4,
        status=MockExamAttemptStatus.IN_PROGRESS,
        started_at=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc),
        submitted_at=None,
        last_active_at=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc),
        current_position=1,
        answered_count=0,
        correct_count=0,
        score_pct=None,
    )

    async def update_attempt(entity, **data):
        for key, value in data.items():
            setattr(entity, key, value)
        return entity

    service.mock_exam_attempt_repo = SimpleNamespace(
        get_by_id_for_user=AsyncMock(return_value=attempt),
        update=AsyncMock(side_effect=update_attempt),
    )
    service.mock_exam_repo = SimpleNamespace(
        get_by_id_with_links=AsyncMock(return_value=exam),
    )
    service._sync_attempt_timeout = AsyncMock(return_value=False)  # noqa: SLF001
    service._refresh_attempt_progress = AsyncMock()  # noqa: SLF001

    result = await service.submit_mock_exam_attempt(1, 21)

    assert result["status"] == "completed"
    assert result["score_pct"] == 0.0
    service._refresh_attempt_progress.assert_awaited_once_with(attempt, exam)


@pytest.mark.asyncio
async def test_submit_mock_exam_attempt_returns_completed_after_expiry() -> None:
    session = AsyncMock()
    service = MockExamService(session=session)
    exam = SimpleNamespace(
        id=4,
        mock_exam_id=4,
        time_limit_minutes=40,
        question_links=[SimpleNamespace(id=9, position=1)],
    )
    attempt = SimpleNamespace(
        id=21,
        mock_exam_id=4,
        status=MockExamAttemptStatus.IN_PROGRESS,
        started_at=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc),
        submitted_at=None,
        last_active_at=datetime(2026, 4, 16, 9, 0, tzinfo=timezone.utc),
        current_position=1,
        answered_count=0,
        correct_count=0,
        score_pct=None,
    )

    async def sync_timeout(entity, _exam):
        entity.status = MockExamAttemptStatus.COMPLETED
        entity.submitted_at = datetime(2026, 4, 16, 9, 40, tzinfo=timezone.utc)
        entity.score_pct = 0.0
        return True

    service.mock_exam_attempt_repo = SimpleNamespace(
        get_by_id_for_user=AsyncMock(return_value=attempt),
    )
    service.mock_exam_repo = SimpleNamespace(
        get_by_id_with_links=AsyncMock(return_value=exam),
    )
    service._sync_attempt_timeout = AsyncMock(side_effect=sync_timeout)  # noqa: SLF001
    service._refresh_attempt_progress = AsyncMock()  # noqa: SLF001

    result = await service.submit_mock_exam_attempt(1, 21)

    assert result["status"] == "completed"
    assert result["submitted_at"] == datetime(2026, 4, 16, 9, 40, tzinfo=timezone.utc)
    service._refresh_attempt_progress.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_mock_exam_uses_assessment_number_family() -> None:
    session = AsyncMock()
    service = MockExamService(session=session)
    payload = SimpleNamespace(
        course_id=2,
        assessment_type=AssessmentType.QUIZ,
        assessment_number=3,
        time_limit_minutes=25,
        instructions="Answer everything.",
        is_active=True,
        questions=[
            SimpleNamespace(question_id=10, position=1, points=1),
            SimpleNamespace(question_id=11, position=2, points=1),
        ],
    )
    created_exam = SimpleNamespace(id=44)
    service._validated_questions = AsyncMock(return_value={})  # noqa: SLF001
    service._create_question_links = AsyncMock()  # noqa: SLF001
    service.get_admin_mock_exam_detail = AsyncMock(return_value={"exam": {"id": 44}})
    service.mock_exam_repo = SimpleNamespace(
        get_latest_version=AsyncMock(return_value=SimpleNamespace(version=2)),
        deactivate_family=AsyncMock(),
        create=AsyncMock(return_value=created_exam),
    )

    result = await service.create_mock_exam(99, payload)

    assert result == {"exam": {"id": 44}}
    service.mock_exam_repo.get_latest_version.assert_awaited_once_with(
        2,
        "quiz",
        3,
        origin=MockExamOrigin.MANUAL,
        visibility_scope=MockExamVisibilityScope.COURSE,
        owner_user_id=None,
    )
    service.mock_exam_repo.deactivate_family.assert_awaited_once_with(
        2,
        "quiz",
        3,
        origin=MockExamOrigin.MANUAL,
        visibility_scope=MockExamVisibilityScope.COURSE,
        owner_user_id=None,
    )
    service.mock_exam_repo.create.assert_awaited_once_with(
        course_id=2,
        assessment_type=AssessmentType.QUIZ,
        assessment_number=3,
        assessment_title="Quiz 3",
        assessment_title_slug="quiz-3",
        title="Quiz 3 Mock 3",
        version=3,
        question_count=2,
        time_limit_minutes=25,
        instructions="Answer everything.",
        origin=MockExamOrigin.MANUAL,
        visibility_scope=MockExamVisibilityScope.COURSE,
        owner_user_id=None,
        assessment_id=None,
        is_active=True,
        created_by_admin_id=99,
    )

@pytest.mark.asyncio
async def test_update_mock_exam_reuses_current_assessment_number_by_default() -> None:
    session = AsyncMock()
    service = MockExamService(session=session)
    current = SimpleNamespace(
        id=12,
        course_id=2,
        assessment_type=AssessmentType.MIDTERM,
        assessment_number=2,
        time_limit_minutes=50,
        instructions="Current instructions",
        is_active=True,
        question_links=[
            SimpleNamespace(question_id=8, position=1, points=1),
        ],
    )
    payload = SimpleNamespace(
        assessment_number=None,
        time_limit_minutes=None,
        instructions=None,
        is_active=None,
        questions=None,
    )
    service._load_mock_exam = AsyncMock(return_value=current)  # noqa: SLF001
    service.create_mock_exam = AsyncMock(return_value={"exam": {"id": 13}})

    result = await service.update_mock_exam(99, 12, payload)

    assert result == {"exam": {"id": 13}}
    service.create_mock_exam.assert_awaited_once()
    request = service.create_mock_exam.await_args.args[1]
    assert request.course_id == 2
    assert request.assessment_type == AssessmentType.MIDTERM
    assert request.assessment_number == 2
    assert request.time_limit_minutes == 50
    assert request.instructions == "Current instructions"
    assert request.is_active is True
    assert len(request.questions) == 1
    assert request.questions[0].question_id == 8
