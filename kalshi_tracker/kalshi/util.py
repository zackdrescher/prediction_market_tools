"""Utilities for kalshi API."""

import kalshi_python
from kalshi_python.models import LoginRequest

from .kalshi_settings import KalshiLoginSettings


def get_kalshi() -> kalshi_python.ApiInstance:
    """Get kalshi API key from environment vairables."""
    from kalshi_tracker.config import Settings

    settings = Settings()
    return kalshi_python.ApiInstance(settings)


def get_kalshi_from_settings(
    settings: KalshiLoginSettings,
) -> kalshi_python.ApiInstance:
    """Get kalshi API key from environment vairables."""
    config = kalshi_python.Configuration()
    config.host = settings.host

    api = kalshi_python.ApiInstance(
        email=settings.email,
        password=settings.password,
        configuration=config,
    )

    # login
    login = api.login(LoginRequest(email=settings.email, password=settings.password))
    api.set_api_token(login.token)

    return api
