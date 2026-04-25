import pytest
from datetime import date
from fastapi import HTTPException

from app.api.validators import validate_currency, validate_date, validate_date_range


def test_validate_currency_valid():
    assert validate_currency("USD") == "USD"
    assert validate_currency("EUR") == "EUR"


def test_validate_currency_invalid_format():
    with pytest.raises(HTTPException) as exc:
        validate_currency("US")
    assert exc.value.status_code == 422


def test_validate_currency_lowercase_rejected():
    with pytest.raises(HTTPException) as exc:
        validate_currency("usd")
    assert exc.value.status_code == 422


def test_validate_currency_unsupported():
    with pytest.raises(HTTPException) as exc:
        validate_currency("XYZ")
    assert exc.value.status_code == 422


def test_validate_date_valid():
    d = date(2024, 1, 15)
    assert validate_date(d) == d


def test_validate_date_too_early():
    with pytest.raises(HTTPException) as exc:
        validate_date(date(2001, 12, 31))
    assert exc.value.status_code == 422


def test_validate_date_future():
    with pytest.raises(HTTPException) as exc:
        validate_date(date(2099, 1, 1))
    assert exc.value.status_code == 422


def test_validate_date_range_valid():
    start = date(2024, 1, 1)
    end = date(2024, 3, 1)
    assert validate_date_range(start, end) == (start, end)


def test_validate_date_range_reversed():
    with pytest.raises(HTTPException) as exc:
        validate_date_range(date(2024, 3, 1), date(2024, 1, 1))
    assert exc.value.status_code == 422


def test_validate_date_range_exceeds_365_days():
    with pytest.raises(HTTPException) as exc:
        validate_date_range(date(2023, 1, 1), date(2024, 12, 31))
    assert exc.value.status_code == 422


def test_validate_date_range_same_day():
    d = date(2024, 6, 15)
    assert validate_date_range(d, d) == (d, d)
