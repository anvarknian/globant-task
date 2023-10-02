from datetime import datetime

from fastapi import APIRouter

from app.celery.worker import get_analytics
from app.models.Models import Response

app = APIRouter()


@app.post("/post_employee_hires_by_quarter",
          response_model=Response,
          name="post_employee_hires_by_quarter")
async def post_employee_hires_by_quarter(year: int) -> Response:
    try:
        task = get_analytics.apply_async(args=[year, 1])
        return Response(status=task.state,
                        msg=f"{task.id}",
                        status_code=200,
                        timestamp=datetime.now().isoformat())
    except Exception as e:
        return Response(status="ERROR",
                        msg=f"{e.__str__()}",
                        status_code=400,
                        timestamp=datetime.now().isoformat())


@app.post("/post_departments_with_above_average_hires",
          response_model=Response,
          name="post_departments_with_above_average_hires")
async def post_departments_with_above_average_hires(year: int) -> Response:
    try:
        task = get_analytics.apply_async(args=[year, 2])
        return Response(status=task.state,
                        msg=f"{task.id}",
                        status_code=200,
                        timestamp=datetime.now().isoformat())
    except Exception as e:
        return Response(status="ERROR",
                        msg=f"{e.__str__()}",
                        status_code=400,
                        timestamp=datetime.now().isoformat())
