"""Tests for the settings module."""

import pytest
from pydantic import ValidationError
from pydantic_settings import SettingsConfigDict

from kalshi_tracker.config import Settings


@pytest.fixture
def no_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    """Create a settings object with no settings."""
    monkeypatch.setattr(Settings, "model_config", SettingsConfigDict(env_file=None))


def test_default_settings(no_settings: None) -> None:
    """Test the default settings."""

    with pytest.raises(ValidationError):
        settings = Settings()
