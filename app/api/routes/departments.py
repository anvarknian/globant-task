import datetime

from fastapi import UploadFile, APIRouter
from prisma.models import departments as departments

from app.celery.worker import insert_records_task
from app.models.Models import Department, Response

app = APIRouter()


@app.post("/file/", response_model=Response, name="batch_upload_departments")
async def upload_departments(file: UploadFile) -> Response:
    try:
        if not file.filename.endswith(".csv"):
            raise Exception(f"Invalid file format {file.filename} - expecting a .csv as input")
        else:
            with open(f"data/departments/{file.filename}", "wb") as f:
                f.write(file.file.read())
                task = insert_records_task.apply_async(args=[file.filename, "departments"])
                return Response(status=task.state,
                                msg="Inserting Data...", task_id=f"{task.id}",
                                status_code=200,
                                timestamp=datetime.datetime.now().isoformat())

    except Exception as e:
        return Response(status="ERROR",
                        msg=f"{e.__str__()}", task_id="",
                        status_code=400,
                        timestamp=datetime.datetime.now().isoformat())


@app.post("/department", response_model=Response, name="post_department")
async def post_department(department: Department) -> Response:
    try:
        await departments.prisma().create(department.dict())
        return Response(
            status="SUCCESS",
            status_code=200,
            msg=f"Department {department.dict()} inserted.", task_id="",
            timestamp=datetime.datetime.now().isoformat())
    except Exception as e:
        return Response(
            status="ERROR",
            status_code=400, task_id="",
            msg=f"{e.__str__()}",
            timestamp=datetime.datetime.now().isoformat())


@app.get("/", response_model=Response, name="get_all_departments")
async def get_departments() -> Response:
    try:
        res = await departments.prisma().find_many()
        return Response(
            status="SUCCESS",
            status_code=200, task_id="",
            msg=res,
            timestamp=datetime.datetime.now().isoformat())
    except Exception as e:
        return Response(
            status="ERROR",
            status_code=400,
            msg=f"{e.__str__()}", task_id="",
            timestamp=datetime.datetime.now().isoformat())
