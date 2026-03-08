"""NBP API client for fetching exchange rates."""
import logging
from datetime import date
from decimal import Decimal
from typing import Optional

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class NBPClientError(Exception):
    """NBP API client error."""

    pass


class NBPNotFoundError(NBPClientError):
    """Rate not found (404 from NBP)."""

    pass


class NBPUnavailableError(NBPClientError):
    """NBP API unavailable (5xx, timeout)."""

    pass


async def fetch_rate(currency: str, rate_date: date) -> Optional[dict]:
    """
    Fetch single rate from NBP API.
    GET /exchangerates/rates/a/{currency}/{date}/
    Returns dict with currency, date, rate or None on 404.
    Raises NBPUnavailableError on 5xx/timeout.
    """
    settings = get_settings()
    url = f"{settings.nbp_api_base_url}/exchangerates/rates/a/{currency}/{rate_date}/"
    async with httpx.AsyncClient(timeout=settings.nbp_request_timeout) as client:
        try:
            response = await client.get(url)
            if response.status_code == 404:
                return None
            if response.status_code >= 500:
                raise NBPUnavailableError(f"NBP returned {response.status_code}")
            response.raise_for_status()
            data = response.json()
            rates = data.get("rates", [])
            if not rates:
                return None
            mid = Decimal(str(rates[0]["mid"]))
            effective_date = date.fromisoformat(rates[0]["effectiveDate"])
            return {
                "currency": currency,
                "date": effective_date,
                "rate": mid,
            }
        except httpx.TimeoutException:
            raise NBPUnavailableError("Przekroczono czas oczekiwania na odpowiedź NBP")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise NBPUnavailableError(str(e))


async def fetch_rates_range(
    currency: str, start_date: date, end_date: date
) -> list[dict]:
    """
    Fetch rates in date range from NBP API.
    GET /exchangerates/rates/a/{currency}/{start}/{end}/
    Returns list of {currency, date, rate}.
    """
    settings = get_settings()
    url = f"{settings.nbp_api_base_url}/exchangerates/rates/a/{currency}/{start_date}/{end_date}/"
    async with httpx.AsyncClient(timeout=settings.nbp_request_timeout) as client:
        try:
            response = await client.get(url)
            if response.status_code == 404:
                return []
            if response.status_code >= 500:
                raise NBPUnavailableError(f"NBP returned {response.status_code}")
            response.raise_for_status()
            data = response.json()
            result = []
            for r in data.get("rates", []):
                result.append({
                    "currency": currency,
                    "date": date.fromisoformat(r["effectiveDate"]),
                    "rate": Decimal(str(r["mid"])),
                })
            return result
        except httpx.TimeoutException:
            raise NBPUnavailableError("Przekroczono czas oczekiwania na odpowiedź NBP")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return []
            raise NBPUnavailableError(str(e))
