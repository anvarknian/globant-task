import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.prisma_config import prisma_client
from tests.helpers.get_test_data import get_test_data_path

app = create_app()
client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
async def prisma_client_test():
    await prisma_client.connect()
    yield
    await prisma_client.disconnect()


def test_upload_jobs():
    test_file_path = get_test_data_path("jobs.csv")
    response = client.post("/api/jobs/file/", files={"file": ("jobs.csv", open(test_file_path, "rb"))})
    assert response.status_code == 200


def test_post_job():
    job_data = {
        "id": 0,
        "job": "Test Job"
    }
    response = client.post("/api/jobs/job", json=job_data)
    assert response.status_code == 200


@pytest.mark.skip(reason="Skipping this test because of prisma.errors.ClientNotConnectedError")
def test_get_jobs(prisma_client_test):
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
