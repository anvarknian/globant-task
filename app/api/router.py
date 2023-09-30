from fastapi import APIRouter, Depends

from app.api.routes import health_check, jobs, departments

api_router = APIRouter()

api_router.include_router(health_check.app, tags=["health"], prefix="/health")

api_router.include_router(jobs.app, tags=["Jobs"], prefix="/jobs")

api_router.include_router(departments.app, tags=["Departments"], prefix="/departments")