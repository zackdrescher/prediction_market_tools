"""Utilities for kalshi API."""

import kalshi_python

from .kalshi_settings import KalshiSettings


def get_kalshi() -> kalshi_python.ApiInstance:
    """Get kalshi API key from environment vairables."""
    from kalshi_tracker.config import Settings

    settings = Settings()
    return kalshi_python.ApiInstance(settings)


def get_kalshi_from_settings(settings: KalshiSettings) -> kalshi_python.ApiInstance:
    """Get kalshi API key from environment vairables."""
    return kalshi_python.ApiInstance(**settings.model_dump())
