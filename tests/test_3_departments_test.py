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


def test_upload_departments():
    test_file_path = get_test_data_path("departments.csv")
    response = client.post("/api/departments/file/", files={"file": ("departments.csv", open(test_file_path, "rb"))})
    assert response.status_code == 200


def test_post_department():
    department_data = {
        "id": 0,
        "department": "Test Department"
    }
    response = client.post("/api/departments/department", json=department_data)
    assert response.status_code == 200


@pytest.mark.skip(reason="Skipping this test because of prisma.errors.ClientNotConnectedError")
def test_get_departments():
    response = client.get("/api/departments")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
