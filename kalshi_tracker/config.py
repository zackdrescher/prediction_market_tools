"""Base settings for the project."""

from __future__ import annotations

from typing import TYPE_CHECKING, Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

if TYPE_CHECKING:
    from kalshi_tracker.kalshi.kalshi_settings import (
        KalshiKeySettings,
        KalshiLoginSettings,
    )


class Settings(BaseSettings):
    """Base settings for the project."""

    # Kalshi API settings
    kalshi_login: KalshiLoginSettings | None
    kalshi_keys: KalshiKeySettings | None

    # loads config fron .env file
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
    )

    @model_validator(mode="after")
    def validate_kalshi_settings(self) -> Self:
        """Validate the Kalshi settings."""
        if not self.kalshi_login and not self.kalshi_keys:
            raise ValueError("Either kalshi_login or kalshi_keys must be provided.")
        if self.kalshi_login and self.kalshi_keys:
            raise ValueError("Only one of kalshi_login or kalshi_keys can be provided.")
        return self
