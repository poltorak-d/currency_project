"""Rate-related Pydantic schemas."""
from datetime import date as date_type
from decimal import Decimal

from pydantic import BaseModel, Field


class RateResponse(BaseModel):
    """Single rate response."""

    currency: str = Field(..., description="Currency code ISO 4217")
    date: date_type = Field(..., description="Rate date")
    rate: Decimal = Field(..., description="Exchange rate vs PLN")

    model_config = {"from_attributes": True}


class RatePoint(BaseModel):
    """Single point for chart/range response."""

    date: date_type
    rate: Decimal


class RateRangeResponse(BaseModel):
    """Range of rates response."""

    currency: str
    rates: list[RatePoint]
