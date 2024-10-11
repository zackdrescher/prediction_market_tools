"""Utilities for kalshi API."""

import os

import dotenv
import kalshi_python


def get_kalshi_api_from_env() -> kalshi_python.ApiClient:
    """Get kalshi API key from environment vairables."""
    dotenv.load_dotenv()
    return kalshi_python.ApiClient(
        email=os.getenv("KALSHI_EMAIL"),
        password=os.getenv("KALSHI_PASSWORD"),
    )
