"""Base settings for the project."""
from pydantic_settings import BaseSettings, SettingsConfigDict

from .kalshi.kalshi_settings import KalshiSettings


class Settings(BaseSettings):
    """Base settings for the project."""

    kalshi: KalshiSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
    )
