from pathlib import Path
import sys
from types import SimpleNamespace

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from nutrack.main import app  # noqa: E402


@pytest.fixture
def current_user() -> SimpleNamespace:
    return SimpleNamespace(
        id=1,
        email="student@nu.edu.kz",
        subscribed_to_notifications=True,
    )


@pytest.fixture
def test_app():
    original = app.dependency_overrides.copy()
    yield app
    app.dependency_overrides = original


@pytest_asyncio.fixture
async def client(test_app):
    transport = ASGITransport(app=test_app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client
