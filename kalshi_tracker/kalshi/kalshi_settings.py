"""Settings for the Kalshi API."""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from pydantic import BaseModel, computed_field

from kalshi_tracker.config import Settings


class KalshiLoginSettings(BaseModel):
    """Login Auth Settings for the Kalshi API."""

    email: str
    password: str
    host: str = "api.elections.kalshi.com/trade-api/v2"


def load_private_key_from_file(file_path: str | Path) -> str:
    """Load a private key from a file."""

    with Path(file_path).open("rb") as key_file:
        return serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # or provide a password if your key is encrypted
            backend=default_backend(),
        )


class KalshiKeySettings(BaseModel):
    """Key Based Auth Settings for the Kalshi API."""

    key: str
    key_file: str
    host: str = "https://api.elections.kalshi.com/trade-api/v2"

    @computed_field
    @property
    def secret(self) -> str:
        """Load the private key from the key file."""
        return load_private_key_from_file(self.key_file)


# update the settings model which refeernces these types
Settings.model_rebuild()
