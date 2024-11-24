import pytest
from fastapi.testclient import TestClient

from kalshi_tracker.api import app


@pytest.fixture
def client_fixture() -> TestClient:
    """Generate a test client for the FastAPI app."""
    return TestClient(app)
