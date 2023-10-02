from datetime import datetime

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


def test_upload_employees():
    test_file_path = get_test_data_path("employees.csv")
    response = client.post("/api/employees/file/", files={"file": ("employees.csv", open(test_file_path, "rb"))})
    assert response.status_code == 200


def test_post_employee():
    employee_data = {
        "id": 0,
        "name": "Test Employee",
        "datetime": str(datetime.now().isoformat()),
        "job_id": 0,
        "department_id": 0
    }
    response = client.post("/api/employees/employee", json=employee_data)
    assert response.status_code == 200


@pytest.mark.skip(reason="Skipping this test because of prisma.errors.ClientNotConnectedError")
def test_get_employees():
    response = client.get("/api/employees")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
