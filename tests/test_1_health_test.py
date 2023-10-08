from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200

    response_data = response.json()

    assert isinstance(response_data, dict)

    assert "is_api_alive" in response_data
    assert response_data["is_api_alive"] is True

    assert "is_db_alive" in response_data
    assert response_data["is_db_alive"] is True
