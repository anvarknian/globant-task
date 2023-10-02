from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200

    response_data = response.json()
    assert "is_alive" in response_data
    assert response_data["is_alive"] is True
