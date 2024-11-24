import pytest
from fastapi.testclient import TestClient

from kalshi_tracker.api import app


@pytest.fixture
def client() -> TestClient:
    """Generate a test client for the FastAPI app."""
    return TestClient(app)


def test_get_markets__returns_data(client: TestClient) -> None:
    """Test the get markets endpoint."""
    response = client.get("/markets")

    assert response.status_code == 200
    assert response.json() == {"markets": ["market1", "market2", "market3"]}
