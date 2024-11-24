"""Get all markets."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class MarketsResponse(BaseModel):
    """Response for `get_markets` endpoint."""

    markets: list[str]


@router.get("/")
async def get_markets() -> MarketsResponse:
    """Get all markets."""
    return MarketsResponse(markets=["market1", "market2", "market3"])
