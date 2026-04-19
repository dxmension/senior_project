from sqlalchemy.orm import configure_mappers

from nutrack.celery_app import celery_app
from nutrack.course_materials.models import CourseMaterialUpload
from nutrack.config import settings
from nutrack.database import get_sync_database_url, load_target_metadata


def test_get_sync_database_url_uses_sync_setting() -> None:
    assert get_sync_database_url() == settings.SYNC_DATABASE_URL


def test_load_target_metadata_registers_domain_tables() -> None:
    metadata = load_target_metadata()

    assert {"users", "courses", "enrollments"}.issubset(metadata.tables)


def test_celery_bootstrap_registers_study_user_relationships() -> None:
    configure_mappers()

    assert "nutrack.course_materials.tasks.upload_course_material_task" in celery_app.tasks
    assert CourseMaterialUpload.uploader.property.mapper.class_.__name__ == "User"
