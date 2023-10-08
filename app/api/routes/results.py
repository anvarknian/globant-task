import datetime

from celery.result import AsyncResult
from fastapi import APIRouter

from app.models.Models import Response

app = APIRouter()


@app.get("/results/",
         response_model=Response,
         name="get_task_result")
async def get_task_result(task_id: str):
    result = f"Task Id: '{task_id}' not found."
    state = 'NOT_FOUND'
    status_code = 400

    if AsyncResult(task_id).successful():
        result = AsyncResult(task_id).get()
        state = AsyncResult(task_id).state
        status_code = 200
    elif AsyncResult(task_id).failed():
        state = AsyncResult(task_id).state
        result = AsyncResult(task_id).traceback
        status_code = 500

    return Response(msg=result,
                    status=state,
                    task_id=f"{task_id}",
                    status_code=status_code,
                    timestamp=datetime.datetime.now().isoformat())
