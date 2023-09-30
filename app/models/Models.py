from pydantic import BaseModel


class Employee(BaseModel):
    id: int
    name: str
    datetime: str
    department_id: int = 0
    job_id: int = 0


class Department(BaseModel):
    id: int
    department: str


class Job(BaseModel):
    id: int
    job: str


class Response(BaseModel):
    status: str
    status_code: int = 200
    msg: str
    timestamp: str
