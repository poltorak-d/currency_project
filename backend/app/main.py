"""FastAPI application entry point."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import currencies, rates
from app.db.init_db import check_db_connection, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup."""
    await init_db()
    ok = await check_db_connection()
    if not ok:
        logger.warning(
            "Database connection check failed — ensure PostgreSQL (local) or Azure SQL is reachable"
        )
    yield
    # shutdown: close connections etc. if needed


app = FastAPI(
    title="Currency Exchange Rates API",
    description="Aplikacja do pobierania i archiwizacji kursów walut z API NBP",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production restrict to frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rates.router)
app.include_router(currencies.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    db_ok = await check_db_connection()
    return {
        "status": "healthy" if db_ok else "degraded",
        "database": "ok" if db_ok else "error",
    }
