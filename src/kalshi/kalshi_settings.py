"""Settings for the Kalshi API."""

from pydantic import BaseModel


class KalshiSettings(BaseModel):
    """Settings for the Kalshi API."""

    email: str
    password: str
