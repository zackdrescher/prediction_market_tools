"""Key Settings for the Kalshi API."""

from __future__ import annotations

from pydantic import BaseModel


class KalshiKeySettings(BaseModel):
    """Key Based Auth Settings for the Kalshi API."""

    key: str
    key_file: str
    host: str = "https://api.elections.kalshi.com/trade-api/v2"
