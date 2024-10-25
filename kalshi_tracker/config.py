"""Base settings for the project."""

from pydantic_settings import BaseSettings, SettingsConfigDict

from kalshi_tracker.kalshi.kalshi_settings import KalshiLoginSettings


class Settings(BaseSettings):
    """Base settings for the project."""

    # Kalshi API settings
    kalshi: KalshiLoginSettings

    # loads config fron .env file
    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        env_file=".env",
    )
