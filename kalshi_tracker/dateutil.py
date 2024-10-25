"""Utility functions for working with dates and times."""

from datetime import datetime


def now_utc() -> datetime:
    """Get the current datetime in UTC."""
    return datetime.now(datetime.timezone.utc)
