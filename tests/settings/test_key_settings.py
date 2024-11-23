"""Tests for the Kalshi key settings."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import dh, rsa
from pydantic import ValidationError
from pytest_mock import MockerFixture

from kalshi_tracker.kalshi.settings import KalshiKeySettings
from kalshi_tracker.kalshi.settings.key_settings import load_private_key_from_file


def test_key_settings__no_settings__raises_validation_error() -> None:
    """Test the key settings with no settings."""
    with pytest.raises(ValidationError):
        settings = KalshiKeySettings()  # type: ignore


def test_key_settings__valid_settings__returns_settings() -> None:
    """Test the key settings with valid settings."""
    settings = KalshiKeySettings(key="test", key_file="test")

    assert settings.key == "test"
    assert settings.key_file == "test"
    assert settings.host == "https://api.elections.kalshi.com/trade-api/v2"


def test_key_settings__secret__returns_secret(mocker: MockerFixture) -> None:
    """Test the key settings secret."""
    mock_rsa_private_key = mocker.Mock(spec=rsa.RSAPrivateKey)
    key_func = mocker.patch(
        "kalshi_tracker.kalshi.settings.key_settings.load_private_key_from_file",
        return_value=mock_rsa_private_key,
    )

    settings = KalshiKeySettings(key="test", key_file="test")
    key_func.assert_not_called()

    assert settings.secret == mock_rsa_private_key
    key_func.assert_called_once_with("test")


def test_load_private_key_from_file__valid_key__successful(
    mocker: MockerFixture,
) -> None:
    """Test the load private key from file with invalid key."""
    # Mock the file opening part
    mock_open = mocker.patch.object(
        Path,
        "open",
        mocker.mock_open(read_data=b"mocked_pem_data"),
    )

    # Mock the deserialization of the private key
    mock_key = MagicMock(rsa.RSAPrivateKey)
    mock_load_pem = mocker.patch.object(
        serialization,
        "load_pem_private_key",
        return_value=mock_key,
    )

    # Call the function with a mock file path
    file_path = Path("mocked_path.pem")
    result = load_private_key_from_file(file_path)

    # Verify the file was opened correctly
    mock_open.assert_called_once_with("rb")

    # Verify that load_pem_private_key was called with the correct data
    mock_load_pem.assert_called_once_with(
        b"mocked_pem_data",
        password=None,
        backend=mocker.ANY,
    )

    # Ensure the result is the mock key we created
    assert result is mock_key


def test_load_private_key_from_file__invalid_key_type__raises_type_error(
    mocker: MockerFixture,
) -> None:
    """Test the load private key from file with invalid key."""

    # Mock the file opening part
    mock_open = mocker.patch.object(
        Path,
        "open",
        mocker.mock_open(read_data=b"mocked_pem_data"),
    )

    # Mock the deserialization of the private key
    mock_key = MagicMock(dh.DHPrivateKey)
    mock_load_pem = mocker.patch.object(
        serialization,
        "load_pem_private_key",
        return_value=mock_key,
    )

    file_path = Path("mocked_path.pem")

    with pytest.raises(TypeError):
        # Call the function with a mock file path
        result = load_private_key_from_file(file_path)

    mock_open.assert_called_once_with("rb")
    # Verify that load_pem_private_key was called with the correct data
    mock_load_pem.assert_called_once_with(
        b"mocked_pem_data",
        password=None,
        backend=mocker.ANY,
    )
