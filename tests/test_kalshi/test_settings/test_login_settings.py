"""Tests for the Kalshi login settings."""

import pytest
from pydantic import ValidationError

from kalshi_tracker.kalshi.settings import KalshiLoginSettings


def test_login_settings__no_settings__raises_validation_error() -> None:
    """Test the login settings with no settings."""
    with pytest.raises(ValidationError):
        settings = KalshiLoginSettings()  # type: ignore


def test_login_settings__valid_settings__returns_settings() -> None:
    """Test the login settings with valid settings."""
    settings = KalshiLoginSettings(email="test", password="test")
    assert settings.email == "test"
    assert settings.password == "test"
    assert settings.host == "api.elections.kalshi.com/trade-api/v2"
