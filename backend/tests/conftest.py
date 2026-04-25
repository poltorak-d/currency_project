import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def db_session():
    return AsyncMock()


@pytest.fixture
async def client(db_session):
    with patch("app.main.init_db", new_callable=AsyncMock), \
         patch("app.main.check_db_connection", new_callable=AsyncMock, return_value=True):
        from app.main import app
        from app.db.database import get_db

        async def _override_db():
            yield db_session

        app.dependency_overrides[get_db] = _override_db
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
        app.dependency_overrides.clear()
