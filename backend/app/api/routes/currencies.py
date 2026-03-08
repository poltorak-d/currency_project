"""Currencies API routes."""
from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix="/currencies", tags=["currencies"])


@router.get("")
async def list_currencies():
    """Lista obsługiwanych walut (tabela A NBP)."""
    return {"currencies": list(get_settings().supported_currencies)}
