from celery import states
from celery.result import AsyncResult
from fastapi import APIRouter
from datetime import datetime
from app.celery.worker import get_analytics
from app.models.Models import Response, EmployeesCountByQuarter, DepartmentsWithAboveAVGHires

app = APIRouter()


@app.post("/post_employee_hires_by_quarter", name="post_employee_hires_by_quarter")
async def post_employee_hires_by_quarter(year: int):
    task = get_analytics.apply_async(args=[year, 1])
    return Response(status=task.state,
                    msg=f"{task.id}",
                    status_code=202,
                    timestamp=datetime.now().isoformat())


@app.get("/get_employee_hires_by_quarter",
         response_model=EmployeesCountByQuarter,
         name="get_employee_hires_by_quarter")
async def get_employee_hires_by_quarter(task_id: str):
    task = AsyncResult(task_id)
    result = task.get()
    response = EmployeesCountByQuarter(**result)
    return response


@app.post("/post_departments_with_above_average_hires", name="post_departments_with_above_average_hires")
async def post_departments_with_above_average_hires(year: int):
    task = get_analytics.apply_async(args=[year, 2])
    return Response(status=task.state,
                    msg=f"{task.id}",
                    status_code=202,
                    timestamp=datetime.now().isoformat())


@app.get("/get_departments_with_above_average_hires",
         response_model=DepartmentsWithAboveAVGHires,
         name="get_departments_with_above_average_hires")
async def get_departments_with_above_average_hires(task_id: str):
    task = AsyncResult(task_id)
    result = task.get()
    response = DepartmentsWithAboveAVGHires(**result)
    return response
