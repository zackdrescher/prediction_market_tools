"""Settings for the Kalshi API."""

from pydantic import BaseModel


class KalshiLoginSettings(BaseModel):
    """Settings for the Kalshi API."""

    email: str
    password: str
    host: str = "api.elections.kalshi.com/trade-api/v2"

    class KalshiKeySettings(BaseModel):
        """Settings for the Kalshi API."""

        key: str
        secret: str
        host: str = "api.elections.kalshi.com/trade-api/v2"
