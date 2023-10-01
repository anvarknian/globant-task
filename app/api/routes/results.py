import datetime

from celery import states
from celery.result import AsyncResult
from fastapi import APIRouter

from app.models.Models import Response

app = APIRouter()


@app.get("/results/", name="get_task_result")
async def get_task_result(task_id: str):
    task = AsyncResult(task_id)
    if task.successful():
        result = task.get()
        state = task.state
        status_code = 200

    else:
        state = states.FAILURE
        status_code = 500
        result = str(task.get().result)

    return Response(msg=result,
                    status=state,
                    status_code=status_code,
                    timestamp=datetime.datetime.now().isoformat())
