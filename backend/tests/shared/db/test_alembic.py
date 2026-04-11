from nutrack.config import settings
from nutrack.database import get_sync_database_url, load_target_metadata


def test_get_sync_database_url_uses_sync_setting() -> None:
    assert get_sync_database_url() == settings.SYNC_DATABASE_URL


def test_load_target_metadata_registers_domain_tables() -> None:
    metadata = load_target_metadata()

    assert {"users", "courses", "enrollments"}.issubset(metadata.tables)
