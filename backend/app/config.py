"""Application configuration."""
from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment."""

    database_url: str = "postgresql+asyncpg://currency:currency_secret@localhost:5432/currency_db"
    redis_url: str = "redis://localhost:6379/0"
    nbp_api_base_url: str = "https://api.nbp.pl/api"
    nbp_request_timeout: int = 10

    # Supported currencies (Table A NBP)
    supported_currencies: tuple = (
        "USD",
        "EUR",
        "CHF",
        "GBP",
        "CZK",
        "DKK",
        "NOK",
        "SEK",
        "JPY",
        "CAD",
    )

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
