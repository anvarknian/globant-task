import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_test_data_path(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)


def test_upload_employees():
    test_file_path = get_test_data_path("employees.csv")
    response = client.post("/employees/file/", files={"file": ("employees.csv", open(test_file_path, "rb"))})
    assert response.status_code == 200


def test_post_employee():
    employee_data = {
        "id": 0,
        "employee": "Test"
    }
    response = client.post("/employees/employee", json=employee_data)
    assert response.status_code == 200


def test_get_employees():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main()
