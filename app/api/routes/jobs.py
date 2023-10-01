import datetime
from typing import List

from fastapi import UploadFile, APIRouter
from prisma.models import jobs as jobs

from app.celery.worker import insert_records_task
from app.models.Models import Job, Response

app = APIRouter()


@app.post("/file/", name="batch_upload_jobs")
async def upload_jobs(file: UploadFile):
    try:
        if not file.filename.endswith(".csv"):
            raise Exception(f"Invalid file format {file.filename} - expecting a .csv as input")
        else:
            with open(f"data/jobs/{file.filename}", "wb") as f:
                f.write(file.file.read())
                task = insert_records_task.apply_async(args=[file.filename, "jobs"])
                return Response(status=task.state,
                                msg=f"{task.id}",
                                status_code=200,
                                timestamp=datetime.datetime.now().isoformat())

    except Exception as e:
        return Response(status="ERROR",
                        msg=f"{e.__str__()}", status_code=400,
                        timestamp=datetime.datetime.now().isoformat())


@app.post("/job", name="post_job")
async def post_job(job: Job):
    try:
        await jobs.prisma().create(job.dict())
        return Response(
            status="SUCCESS",
            msg=f"Job {job.dict()} inserted.",
            timestamp=datetime.datetime.now().isoformat())
    except Exception as e:
        return Response(
            status="ERROR",
            msg=f"{e.__str__()}", status_code=400,
            timestamp=datetime.datetime.now().isoformat())


@app.get("/", response_model=List[Job], name="get_all_jobs")
async def get_jobs():
    return await jobs.prisma().find_many()
