from pathlib import Path

from sqlalchemy.orm import configure_mappers

from nutrack.celery_app import celery_app
from nutrack.course_materials.models import CourseMaterialUpload
from nutrack.config import settings
from nutrack.database import get_sync_database_url, load_target_metadata


def test_get_sync_database_url_uses_sync_setting() -> None:
    assert get_sync_database_url() == settings.SYNC_DATABASE_URL


def test_load_target_metadata_registers_domain_tables() -> None:
    metadata = load_target_metadata()

    assert {
        "users",
        "courses",
        "enrollments",
        "handbook_plans",
    }.issubset(metadata.tables)


def test_celery_bootstrap_registers_study_user_relationships() -> None:
    configure_mappers()

    assert "nutrack.course_materials.tasks.upload_course_material_task" in celery_app.tasks
    assert "nutrack.mindmaps.tasks.generate_mindmap_task" in celery_app.tasks
    assert CourseMaterialUpload.uploader.property.mapper.class_.__name__ == "User"


def test_latest_alembic_revision_repairs_user_schema_drift() -> None:
    revision_path = (
        Path(__file__).resolve().parents[3]
        / "alembic"
        / "versions"
        / "20260419_0009_users_profile_columns.py"
    )

    contents = revision_path.read_text(encoding="utf-8")

    assert 'revision: str = "20260419_0009"' in contents
    assert 'down_revision: Union[str, None] = "20260419_0008"' in contents
    assert '"kazakh_level"' in contents
    assert '"enrollment_year"' in contents


def test_latest_alembic_revision_creates_handbook_plans() -> None:
    revision_path = (
        Path(__file__).resolve().parents[3]
        / "alembic"
        / "versions"
        / "20260419_0010_handbook_plans.py"
    )

    contents = revision_path.read_text(encoding="utf-8")

    assert 'revision: str = "20260419_0010"' in contents
    assert 'down_revision: Union[str, None] = "20260419_0009"' in contents
    assert 'op.create_table(' in contents
    assert '"handbook_plans"' in contents
