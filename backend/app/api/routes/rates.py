"""Rates API routes."""
from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import validate_currency, validate_date, validate_date_range
from app.db.database import get_db
from app.schemas.rate import RatePoint, RateRangeResponse, RateResponse
from app.services.nbp_client import NBPUnavailableError
from app.services.rate_service import get_rate, get_rates_range

router = APIRouter(prefix="/rates", tags=["rates"])


@router.get(
    "/{currency}",
    response_model=RateResponse,
    responses={
        404: {"description": "Brak notowania dla wybranej daty"},
        422: {"description": "Nieprawidłowe parametry"},
        503: {"description": "API NBP niedostępne"},
        504: {"description": "Timeout NBP"},
    },
)
async def get_single_rate(
    currency: str,
    date_param: date = Query(..., alias="date", description="Data w formacie YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    """Pobierz kurs waluty dla danej daty."""
    currency = validate_currency(currency)
    date_param = validate_date(date_param)

    try:
        result = await get_rate(db, currency, date_param)
    except NBPUnavailableError as e:
        if "timeout" in str(e).lower() or "czas" in str(e).lower():
            from fastapi import HTTPException

            raise HTTPException(status_code=504, detail=str(e))
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="API NBP jest chwilowo niedostępne. Spróbuj później.",
        )

    if result is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Brak notowania dla wybranej daty",
        )

    return RateResponse(**result)


@router.get(
    "/{currency}/range",
    response_model=RateRangeResponse,
    responses={
        422: {"description": "Nieprawidłowe parametry"},
        503: {"description": "API NBP niedostępne"},
    },
)
async def get_rates_in_range(
    currency: str,
    start_date: date = Query(..., description="Data początkowa YYYY-MM-DD"),
    end_date: date = Query(..., description="Data końcowa YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db),
):
    """Pobierz kursy w zakresie dat (dla wykresu)."""
    currency = validate_currency(currency)
    start_date, end_date = validate_date_range(start_date, end_date)

    try:
        results = await get_rates_range(db, currency, start_date, end_date)
    except NBPUnavailableError:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=503,
            detail="API NBP jest chwilowo niedostępne. Spróbuj później.",
        )

    rates = [RatePoint(date=r["date"], rate=r["rate"]) for r in results]
    return RateRangeResponse(currency=currency, rates=rates)
