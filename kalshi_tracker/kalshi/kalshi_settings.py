"""Settings for the Kalshi API."""

from __future__ import annotations

from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from pydantic import BaseModel, computed_field

from kalshi_tracker.config import Settings


class KalshiLoginSettings(BaseModel):
    """Login Auth Settings for the Kalshi API."""

    email: str
    password: str
    host: str = "api.elections.kalshi.com/trade-api/v2"


def load_private_key_from_file(file_path: str | Path) -> RSAPrivateKey:
    """Load a private key from a file."""

    with Path(file_path).open("rb") as key_file:
        key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # or provide a password if your key is encrypted
            backend=default_backend(),
        )

    if not isinstance(key, RSAPrivateKey):
        raise TypeError("Key at {file_path} is not an RSA private key")

    return key


class KalshiKeySettings(BaseModel):
    """Key Based Auth Settings for the Kalshi API."""

    key: str
    key_file: str
    host: str = "https://api.elections.kalshi.com/trade-api/v2"

    @computed_field
    @property
    def secret(self) -> RSAPrivateKey:
        """Load the private key from the key file."""
        return load_private_key_from_file(self.key_file)

    class Config:
        """Pydantic model configuration."""

        arbitrary_types_allowed = True


# update the settings model which refeernces these types
Settings.model_rebuild()
