"""Utility functions for working with dates and times."""

import datetime


def now_utc() -> datetime.datetime:
    """Get the current datetime in UTC."""
    return datetime.datetime.now(datetime.timezone.utc)
