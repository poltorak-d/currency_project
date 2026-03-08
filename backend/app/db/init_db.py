"""Database initialization - create tables."""
import asyncio

from sqlalchemy import text

from app.db.database import Base, engine
from app.models import ExchangeRate  # noqa: F401 - register models


async def init_db() -> None:
    """Create all tables in the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_db_connection() -> bool:
    """Verify database connection."""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
