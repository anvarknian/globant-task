from typing import List, Any

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
    task_id: str
    msg: Any
    timestamp: str


class EmployeeCountByQuarter(BaseModel):
    department: str
    job: str
    Q1: int
    Q2: int
    Q3: int
    Q4: int


class EmployeesCountByQuarter(BaseModel):
    employees: List[EmployeeCountByQuarter]

    def to_dict(self):
        return {
            "employees": [employee.dict() for employee in self.employees]
        }


class DepartmentWithAboveAVGHires(BaseModel):
    id: int
    department: str
    hired: int


class DepartmentsWithAboveAVGHires(BaseModel):
    departments_with_above_avg_hires: List[DepartmentWithAboveAVGHires]

    def to_dict(self):
        return {
            "departments_with_above_avg_hires": [department_with_above_avg_hires.dict() for
                                                 department_with_above_avg_hires in
                                                 self.departments_with_above_avg_hires]
        }
