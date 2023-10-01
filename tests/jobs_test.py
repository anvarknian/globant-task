import os
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_test_data_path(filename):
    return os.path.join(os.path.dirname(__file__), "data", filename)


def test_upload_jobs():
    test_file_path = get_test_data_path("jobs.csv")
    response = client.post("/jobs/file/", files={"file": ("jobs.csv", open(test_file_path, "rb"))})
    assert response.status_code == 200


def test_post_job():
    job_data = {
        "id": 0,
        "job": "Test"
    }
    response = client.post("/jobs/job", json=job_data)
    assert response.status_code == 200


def test_get_jobs():
    response = client.get("/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    pytest.main()
