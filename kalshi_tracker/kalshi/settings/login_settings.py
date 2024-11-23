"""Login Auth Settings for the Kalshi API."""

from pydantic import BaseModel


class KalshiLoginSettings(BaseModel):
    """Login Auth Settings for the Kalshi API."""

    email: str
    password: str
    host: str = "api.elections.kalshi.com/trade-api/v2"
