from fastapi import APIRouter
from pydantic import BaseModel

from app.celery.db import DatabaseConnection

app = APIRouter()


def is_mysql_alive():
    db = DatabaseConnection()
    res = db.is_connected()
    db.conn.close()
    return res


class HeartbeatResult(BaseModel):
    is_api_alive: bool
    is_mysql_alive: bool


@app.get("/", response_model=HeartbeatResult, name="health_check")
def get_healthcheck() -> HeartbeatResult:
    return HeartbeatResult(
        is_api_alive=True,
        is_mysql_alive=is_mysql_alive())
