import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_test_data_path(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)


def test_upload_departments():
    test_file_path = get_test_data_path("departments.csv")
    response = client.post("/departments/file/", files={"file": ("departments.csv", open(test_file_path, "rb"))})
    assert response.status_code == 200


def test_post_department():
    department_data = {
        "id": 0,
        "department": "Test"
    }
    response = client.post("/departments/department", json=department_data)
    assert response.status_code == 200


def test_get_departments():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main()
