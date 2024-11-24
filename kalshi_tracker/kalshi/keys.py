from pathlib import Path

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


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
