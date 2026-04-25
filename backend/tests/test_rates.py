from decimal import Decimal
from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

_RATE = {"currency": "USD", "date": date(2024, 1, 15), "rate": Decimal("3.9500")}
_RANGE = [
    {"currency": "USD", "date": date(2024, 1, 15), "rate": Decimal("3.9500")},
    {"currency": "USD", "date": date(2024, 1, 16), "rate": Decimal("3.9600")},
]


async def test_get_rate_success(client):
    with patch("app.api.routes.rates.get_rate", new_callable=AsyncMock, return_value=_RATE):
        r = await client.get("/rates/USD?date=2024-01-15")
    assert r.status_code == 200
    body = r.json()
    assert body["currency"] == "USD"
    assert body["date"] == "2024-01-15"
    assert float(body["rate"]) == pytest.approx(3.95)


async def test_get_rate_not_found(client):
    with patch("app.api.routes.rates.get_rate", new_callable=AsyncMock, return_value=None):
        r = await client.get("/rates/USD?date=2024-01-15")
    assert r.status_code == 404


async def test_get_rate_invalid_currency(client):
    r = await client.get("/rates/INVALID?date=2024-01-15")
    assert r.status_code == 422


async def test_get_rate_unsupported_currency(client):
    r = await client.get("/rates/XYZ?date=2024-01-15")
    assert r.status_code == 422


async def test_get_rate_future_date(client):
    r = await client.get("/rates/USD?date=2099-01-01")
    assert r.status_code == 422


async def test_get_rate_missing_date(client):
    r = await client.get("/rates/USD")
    assert r.status_code == 422


async def test_get_rates_range_success(client):
    with patch("app.api.routes.rates.get_rates_range", new_callable=AsyncMock, return_value=_RANGE):
        r = await client.get("/rates/USD/range?start_date=2024-01-15&end_date=2024-01-16")
    assert r.status_code == 200
    body = r.json()
    assert body["currency"] == "USD"
    assert len(body["rates"]) == 2
    assert body["rates"][0]["date"] == "2024-01-15"


async def test_get_rates_range_empty(client):
    with patch("app.api.routes.rates.get_rates_range", new_callable=AsyncMock, return_value=[]):
        r = await client.get("/rates/USD/range?start_date=2024-01-15&end_date=2024-01-16")
    assert r.status_code == 200
    assert r.json()["rates"] == []


async def test_get_rates_range_reversed_dates(client):
    r = await client.get("/rates/USD/range?start_date=2024-01-16&end_date=2024-01-15")
    assert r.status_code == 422


async def test_get_rates_range_exceeds_365_days(client):
    r = await client.get("/rates/USD/range?start_date=2023-01-01&end_date=2024-12-31")
    assert r.status_code == 422


async def test_health_check(client):
    r = await client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in ("healthy", "degraded")
    assert "database" in body
