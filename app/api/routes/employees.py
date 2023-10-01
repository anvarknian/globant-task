import datetime
from typing import List

from fastapi import UploadFile, APIRouter
from prisma.models import employees as employees

from app.celery.worker import insert_records_task
from app.models.Models import Employee, Response

app = APIRouter()


@app.post("/file/", name="batch_upload_employees")
async def upload_employees(file: UploadFile):
    try:
        if not file.filename.endswith(".csv"):
            raise Exception(f"Invalid file format {file.filename} - expecting a .csv as input")
        else:
            with open(f"data/employees/{file.filename}", "wb") as f:
                f.write(file.file.read())
                task = insert_records_task.apply_async(args=[file.filename, "employees"])
                return Response(status=task.state,
                                msg=f"{task.id}",
                                status_code=200,
                                timestamp=datetime.datetime.now().isoformat())

    except Exception as e:
        return Response(status="ERROR",
                        msg=f"{e.__str__()}", status_code=400,
                        timestamp=datetime.datetime.now().isoformat())


@app.post("/employee", name="post_employee")
async def post_employee(employee: Employee):
    try:
        await employees.prisma().create(employee.dict())
        return Response(
            status="SUCCESS",
            msg=f"Employee {employee.dict()} inserted.",
            timestamp=datetime.datetime.now().isoformat())
    except Exception as e:
        return Response(
            status="ERROR",
            msg=f"{e.__str__()}", status_code=400,
            timestamp=datetime.datetime.now().isoformat())


@app.get("/", response_model=List[Employee], name="get_all_employees")
async def get_employees():
    return await employees.prisma().find_many()
