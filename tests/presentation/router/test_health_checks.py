from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_success():
    response = client.get(
        "/v1/health-checks",
    )

    assert response.status_code == 200
    assert "ok" in response.json()["status"]
