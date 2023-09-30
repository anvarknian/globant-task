from fastapi import APIRouter
from pydantic import BaseModel

app = APIRouter()


class HearbeatResult(BaseModel):
    is_alive: bool


@app.get("/health", response_model=HearbeatResult, name="health_check")
def get_healthcheck() -> HearbeatResult:
    return HearbeatResult(is_alive=True)
