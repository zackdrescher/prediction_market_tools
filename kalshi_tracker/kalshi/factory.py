"""Factory Methods for kalshi API."""

from __future__ import annotations

from .client.exchange_client import ExchangeClient
from .keys import load_private_key_from_file
from .settings.key_settings import KalshiKeySettings


def get_kalshi() -> ExchangeClient:
    """Get kalshi API key from environment vairables."""
    from kalshi_tracker import config

    settings = config.Settings()

    if settings.kalshi_keys is None:
        raise ValueError("Kalshi keys are not set")

    return get_kalshi_from_settings(settings.kalshi_keys)


def get_kalshi_from_settings(settings: KalshiKeySettings) -> ExchangeClient:
    """Get kalshi API client from key settings."""

    private_key = load_private_key_from_file(settings.key_file)

    return ExchangeClient(
        exchange_api_base=settings.host,
        key_id=settings.key,
        private_key=private_key,
    )
