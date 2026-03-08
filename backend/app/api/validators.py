"""Request validation utilities."""
import re
from datetime import date
from typing import Optional

from fastapi import HTTPException

from app.config import get_settings

CURRENCY_REGEX = re.compile(r"^[A-Z]{3}$")
MAX_RANGE_DAYS = 365
NBP_TABLE_A_START = date(2002, 1, 2)


def validate_currency(currency: str) -> str:
    """Validate currency code (ISO 4217, whitelist)."""
    if not CURRENCY_REGEX.match(currency):
        raise HTTPException(
            status_code=422,
            detail="Nieprawidłowy kod waluty. Użyj formatu ISO 4217 (np. USD, EUR).",
        )
    currency = currency.upper()
    if currency not in get_settings().supported_currencies:
        raise HTTPException(
            status_code=422,
            detail=f"Nieobsługiwana waluta. Dostępne: {', '.join(get_settings().supported_currencies)}",
        )
    return currency


def validate_date(d: date, param_name: str = "date") -> date:
    """Validate date is within NBP Table A range and not in future."""
    if d < NBP_TABLE_A_START:
        raise HTTPException(
            status_code=422,
            detail=f"Data musi być nie wcześniejsza niż {NBP_TABLE_A_START}.",
        )
    if d > date.today():
        raise HTTPException(
            status_code=422,
            detail="Data nie może być w przyszłości.",
        )
    return d


def validate_date_range(start_date: date, end_date: date) -> tuple[date, date]:
    """Validate start <= end and range <= 365 days."""
    if start_date > end_date:
        raise HTTPException(
            status_code=422,
            detail="Data początkowa musi być nie późniejsza niż data końcowa.",
        )
    if (end_date - start_date).days > MAX_RANGE_DAYS:
        raise HTTPException(
            status_code=422,
            detail=f"Zakres dat nie może przekraczać {MAX_RANGE_DAYS} dni.",
        )
    validate_date(start_date, "start_date")
    validate_date(end_date, "end_date")
    return start_date, end_date
