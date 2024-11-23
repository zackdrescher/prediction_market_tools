"""Utilities for kalshi API."""

from .kalshi_client import ExchangeClient
from .kalshi_settings import KalshiKeySettings


def get_kalshi() -> ExchangeClient:
    """Get kalshi API key from environment vairables."""
    from kalshi_tracker import config

    settings = config.Settings()

    if settings.kalshi_keys is None:
        raise ValueError("Kalshi keys are not set")

    return get_kalshi_from_settings(settings.kalshi_keys)


def get_kalshi_from_settings(settings: KalshiKeySettings) -> ExchangeClient:
    """Get kalshi API client from key settings."""
    return ExchangeClient(
        exchange_api_base=settings.host,
        key_id=settings.key,
        private_key=settings.secret,
    )
