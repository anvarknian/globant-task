import datetime
from typing import List

from fastapi import UploadFile, APIRouter
from prisma.models import departments as departments

from app.celery.worker import insert_records_task
from app.models.Models import Department, Response

app = APIRouter()


@app.post("/file/", name="batch_upload_departments")
async def upload_departments(file: UploadFile):
    try:
        if not file.filename.endswith(".csv"):
            raise Exception(f"Invalid file format {file.filename} - expecting a .csv as input")
        else:
            with open(f"data/departments/{file.filename}", "wb") as f:
                f.write(file.file.read())
                task = insert_records_task.apply_async(args=[file.filename, "departments"])
                return Response(status=task.state,
                                msg=f"{task.id}",
                                status_code=200,
                                timestamp=datetime.datetime.now().isoformat())

    except Exception as e:
        return Response(status="ERROR",
                        msg=f"{e.__str__()}", status_code=400,
                        timestamp=datetime.datetime.now().isoformat())


@app.post("/department", name="post_department")
async def post_department(department: Department):
    try:
        await departments.prisma().create(department.dict())
        return Response(
            status="SUCCESS",
            msg=f"Department {department.dict()} inserted.",
            timestamp=datetime.datetime.now().isoformat())
    except Exception as e:
        return Response(
            status="ERROR",
            status_code=400,
            msg=f"{e.__str__()}",
            timestamp=datetime.datetime.now().isoformat())


@app.get("/", response_model=List[Department], name="get_all_departments")
async def get_departments():
    return await departments.prisma().find_many()
