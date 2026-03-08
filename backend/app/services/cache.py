"""Redis cache wrapper for exchange rates."""
import json
import logging
from datetime import date
from decimal import Decimal
from typing import Optional

import redis.asyncio as redis

from app.config import get_settings

logger = logging.getLogger(__name__)

CACHE_TTL = 86400  # 24 hours
CACHE_KEY_PREFIX = "rate"


async def get_redis_client() -> redis.Redis:
    """Create Redis client."""
    return redis.from_url(get_settings().redis_url, decode_responses=True)


async def get_cached_rate(currency: str, rate_date: date) -> Optional[dict]:
    """
    Get rate from cache if present.
    Returns dict with currency, date, rate or None on miss.
    """
    try:
        client = await get_redis_client()
        key = f"{CACHE_KEY_PREFIX}:{currency}:{rate_date}"
        data = await client.get(key)
        await client.aclose()
        if data:
            parsed = json.loads(data)
            parsed["rate"] = Decimal(str(parsed["rate"]))
            parsed["date"] = date.fromisoformat(parsed["date"])
            return parsed
    except Exception as e:
        logger.warning("Redis cache get failed: %s", e)
    return None


async def set_cached_rate(currency: str, rate_date: date, rate: Decimal) -> None:
    """Store rate in cache with TTL."""
    try:
        client = await get_redis_client()
        key = f"{CACHE_KEY_PREFIX}:{currency}:{rate_date}"
        value = json.dumps({
            "currency": currency,
            "date": rate_date.isoformat(),
            "rate": str(rate),
        })
        await client.setex(key, CACHE_TTL, value)
        await client.aclose()
    except Exception as e:
        logger.warning("Redis cache set failed: %s", e)
