from fastapi import APIRouter
from pydantic import BaseModel

app = APIRouter()


class HeartbeatResult(BaseModel):
    is_alive: bool


@app.get("/", response_model=HeartbeatResult, name="health_check")
def get_healthcheck() -> HeartbeatResult:
    return HeartbeatResult(is_alive=True)
