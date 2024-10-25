"""Represents an HTTP error with reason and status code."""


class HttpError(Exception):
    """Represents an HTTP error with reason and status code."""

    def __init__(self, reason: str, status: int) -> None:
        """Initialize the error with a reason and status code."""
        super().__init__(reason)
        self.reason = reason
        self.status = status

    def __str__(self) -> str:
        """Return a string representation of the error."""
        return "HttpError(%d %s)" % (self.status, self.reason)
