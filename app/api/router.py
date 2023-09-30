from fastapi import APIRouter

from app.api.routes import health_check, jobs, departments, employees, results

api_router = APIRouter()

api_router.include_router(health_check.app, tags=["health"], prefix="/health")

api_router.include_router(results.app, tags=["results"], prefix="/result")

api_router.include_router(jobs.app, tags=["Jobs"], prefix="/jobs")

api_router.include_router(departments.app, tags=["Departments"], prefix="/departments")
api_router.include_router(employees.app, tags=["Employees"], prefix="/employees")
