"""Exchange rate model."""
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String, UniqueConstraint, Index, text
from sqlalchemy.types import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class ExchangeRate(Base):
    """Exchange rate record from NBP Table A."""

    __tablename__ = "exchange_rates"
    __table_args__ = (
        UniqueConstraint("currency", "rate_date", name="uq_exchange_rates_currency_rate_date"),
        Index("idx_exchange_rates_currency_date", "currency", "rate_date"),
        Index("idx_exchange_rates_rate_date", "rate_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    rate: Mapped[Decimal] = mapped_column(Numeric(10, 4), nullable=False)
    rate_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return f"<ExchangeRate {self.currency} {self.rate_date} = {self.rate}>"
