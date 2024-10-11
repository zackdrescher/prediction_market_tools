"""Utilities for kalshi API."""

import kalshi_python

from .kalshi_settings import KalshiSettings


def get_kalshi(settings: KalshiSettings) -> kalshi_python.ApiClient:
    """Get kalshi API key from environment vairables."""
    return kalshi_python.ApiClient(**settings.model_dump())
