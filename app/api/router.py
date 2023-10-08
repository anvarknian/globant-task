from fastapi import APIRouter

from app.api.routes import health_check, jobs, departments, employees, results, analytics

api_router = APIRouter()

api_router.include_router(health_check.app, tags=["Health"], prefix="/health")

api_router.include_router(results.app, tags=["Results"], prefix="/results")

api_router.include_router(analytics.app, tags=["Analytics"], prefix="/analytics")

api_router.include_router(jobs.app, tags=["Jobs"], prefix="/jobs")

api_router.include_router(departments.app, tags=["Departments"], prefix="/departments")
api_router.include_router(employees.app, tags=["Employees"], prefix="/employees")
