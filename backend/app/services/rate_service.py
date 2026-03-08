"""Rate service - Cache-Aside logic: Redis -> DB -> NBP API."""
import logging
from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ExchangeRate
from app.services.cache import get_cached_rate, set_cached_rate
from app.services.nbp_client import (
    NBPUnavailableError,
    fetch_rate,
    fetch_rates_range,
)

logger = logging.getLogger(__name__)


async def _get_rate_for_date(
    db: AsyncSession, currency: str, rate_date: date
) -> Optional[dict]:
    """
    Get rate for a single date (no weekend fallback).
    Used internally.
    """
    cached = await get_cached_rate(currency, rate_date)
    if cached:
        return cached

    stmt = select(ExchangeRate).where(
        ExchangeRate.currency == currency,
        ExchangeRate.rate_date == rate_date,
    )
    result = await db.execute(stmt)
    row = result.scalar_one_or_none()
    if row:
        data = {"currency": row.currency, "date": row.rate_date, "rate": row.rate}
        await set_cached_rate(currency, rate_date, row.rate)
        return data

    try:
        data = await fetch_rate(currency, rate_date)
    except NBPUnavailableError:
        raise

    if data is None:
        return None

    record = ExchangeRate(
        currency=data["currency"],
        rate=data["rate"],
        rate_date=data["date"],
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    await set_cached_rate(currency, rate_date, data["rate"])
    return data


async def get_rate(
    db: AsyncSession, currency: str, rate_date: date
) -> Optional[dict]:
    """
    Get rate using Cache-Aside: Redis -> DB -> NBP API.
    For weekend dates, returns average of Friday before and Monday after.
    Returns dict with currency, date, rate or None if not found.
    """
    # 1. Check Redis cache
    cached = await get_cached_rate(currency, rate_date)
    if cached:
        return cached

    w = rate_date.weekday()  # 0=Mon .. 5=Sat, 6=Sun

    if w == 5 or w == 6:  # Saturday or Sunday
        friday = rate_date - timedelta(days=1 if w == 5 else 2)
        monday = rate_date + timedelta(days=2 if w == 5 else 1)

        if monday > date.today():
            return None

        friday_data = await _get_rate_for_date(db, currency, friday)
        monday_data = await _get_rate_for_date(db, currency, monday)

        if friday_data and monday_data:
            avg = (friday_data["rate"] + monday_data["rate"]) / 2
            result = {
                "currency": currency,
                "date": rate_date,
                "rate": Decimal(str(round(float(avg), 4))),
            }
            await set_cached_rate(currency, rate_date, result["rate"])
            return result
        return None

    return await _get_rate_for_date(db, currency, rate_date)


async def get_rates_range(
    db: AsyncSession, currency: str, start_date: date, end_date: date
) -> list[dict]:
    """
    Get rates in range. First from DB, fill gaps from NBP.
    Returns list of {currency, date, rate} sorted by date.
    """
    # 1. Get from DB
    stmt = (
        select(ExchangeRate)
        .where(
            ExchangeRate.currency == currency,
            ExchangeRate.rate_date >= start_date,
            ExchangeRate.rate_date <= end_date,
        )
        .order_by(ExchangeRate.rate_date)
    )
    result = await db.execute(stmt)
    rows = result.scalars().all()
    db_dates = {r.rate_date: r for r in rows}
    db_results = [
        {"currency": r.currency, "date": r.rate_date, "rate": r.rate}
        for r in rows
    ]

    # 2. Fetch from NBP (NBP returns only trading days)
    try:
        nbp_rates = await fetch_rates_range(currency, start_date, end_date)
    except NBPUnavailableError:
        if db_results:
            return db_results
        raise

    if not nbp_rates:
        return db_results

    # 3. Merge: prefer NBP, fill from DB for any missing
    by_date = {r["date"]: r for r in nbp_rates}
    for d, r in db_dates.items():
        if d not in by_date:
            by_date[d] = {"currency": r.currency, "date": r.rate_date, "rate": r.rate}

    # 4. Bulk insert new rates to DB and cache
    for r in nbp_rates:
        if r["date"] not in db_dates:
            record = ExchangeRate(
                currency=r["currency"],
                rate=r["rate"],
                rate_date=r["date"],
            )
            db.add(record)
            await set_cached_rate(r["currency"], r["date"], r["rate"])

    sorted_dates = sorted(by_date.keys())
    return [by_date[d] for d in sorted_dates]
