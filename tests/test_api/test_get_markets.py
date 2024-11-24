from fastapi.testclient import TestClient

from .fixtures import client_fixture  # noqa: F401


def test_get_markets__returns_data(client_fixture: TestClient) -> None:
    """Test the get markets endpoint."""
    response = client_fixture.get("/markets")

    assert response.status_code == 200
    assert response.json() == {"markets": ["market1", "market2", "market3"]}
