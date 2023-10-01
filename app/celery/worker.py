import csv
import logging
import os

from celery import Celery
from psycopg2 import pool

from app.models.Models import Employee, Department, Job, EmployeeCountByQuarter, EmployeesCountByQuarter, \
    DepartmentsWithAboveAVGHires, DepartmentWithAboveAVGHires

logger = logging.getLogger(__name__)

db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    database="globant",
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432"
)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379")


def validate_records(records, model_type):
    validated_records = []
    for record in records:
        try:
            if model_type == "employees":
                validated_record = Employee(
                    id=int(record[0]),
                    name=record[1],
                    datetime=record[2],
                    department_id=int(record[3]),
                    job_id=int(record[4])
                )
            elif model_type == "departments":
                validated_record = Department(
                    id=int(record[0]),
                    department=record[1]
                )
            elif model_type == "jobs":
                validated_record = Job(
                    id=int(record[0]),
                    job=record[1]
                )
            validated_records.append(validated_record)
        except Exception as e:
            logger.error("Validation error for record: %s", e.__str__())
            continue

    return validated_records


def get_connection():
    try:
        connection = db_pool.getconn()
        return connection
    except Exception as e:
        logger.error("Error getting a database connection: %s", str(e))
        raise


def read_csv(file_path):
    with open(file_path, "r") as file:
        csv_reader = csv.reader(file, delimiter=',')
        return list(csv_reader)


def insert_records(records, table_name, model_fields, connection):
    batch_size = 1000
    try:
        cursor = connection.cursor()
        placeholders = ', '.join(['%s'] * len(model_fields))
        columns = ', '.join(model_fields)
        records_to_insert = [tuple(record) for record in records]
        for i in range(0, len(records_to_insert), batch_size):
            batch_data = records_to_insert[i:i + batch_size]
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.executemany(query, batch_data)
            connection.commit()
    except Exception as e:
        connection.rollback()
        logger.error("Error inserting records: %s", str(e))
        raise
    finally:
        cursor.close()


def insert_data_from_csv(file_name, model_type):
    connection = get_connection()
    table_name = model_type
    model_fields = None
    full_file_path = f"data/{model_type}/{file_name}"
    tables = ['employees', 'jobs', 'departments']

    if model_type == "jobs":
        model_fields = ["id", "job"]

    if model_type == "departments":
        model_fields = ["id", "department"]

    if model_type == "employees":
        model_fields = ["id", "name", "datetime", "department_id", "job_id"]

    if table_name not in tables or model_fields is None:
        raise ValueError(f"Invalid model_type - {model_type}")

    csv_data = read_csv(full_file_path)
    if len(csv_data) == 0:
        return

    try:
        records = [row for row in csv_data]
        validated_records = validate_records(records, model_type)
        records_to_insert = [list(record.dict().values()) for record in validated_records]
        insert_records(records_to_insert, table_name, model_fields, connection)
        return (len(records), len(validated_records))
    finally:
        db_pool.putconn(connection)


@celery.task(name="insert_records")
def insert_records_task(file_name, model_type):
    try:
        s, i = insert_data_from_csv(file_name, model_type)
        return f"Sent: {s} ~ Inserted: {i} ~ Ignored: {s - i}"
    except Exception as e:
        logger.error("Error in insert_records_task: %s", str(e))
        raise e


@celery.task(name="get_analytics")
def get_analytics(year: int, query: int):
    response = None
    connection = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        if query == 1:
            sql_query = f"""
            SELECT
                d.department,
                j.job,
                SUM(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(e.datetime, 'YYYY-MM-DD')) = 1 THEN 1 ELSE 0 END) AS Q1,
                SUM(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(e.datetime, 'YYYY-MM-DD')) = 2 THEN 1 ELSE 0 END) AS Q2,
                SUM(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(e.datetime, 'YYYY-MM-DD')) = 3 THEN 1 ELSE 0 END) AS Q3,
                SUM(CASE WHEN EXTRACT(QUARTER FROM TO_DATE(e.datetime, 'YYYY-MM-DD')) = 4 THEN 1 ELSE 0 END) AS Q4
            FROM employees AS e
            LEFT JOIN public.departments AS d ON d.id = e.department_id
            LEFT JOIN public.jobs AS j ON j.id = e.job_id
            WHERE TO_DATE(e.datetime, 'YYYY-MM-DD') BETWEEN '{year}-01-01' AND '{year}-12-31'
            GROUP BY d.department, j.job
            ORDER BY d.department ASC, j.job ASC;
            """

            cursor.execute(sql_query)

            results = cursor.fetchall()
            response = EmployeesCountByQuarter(
                employees=[
                    EmployeeCountByQuarter(
                        department=row[0],
                        job=row[1],
                        Q1=row[2],
                        Q2=row[3],
                        Q3=row[4],
                        Q4=row[5]) for row in results
                ]).to_dict()
        elif query == 2:
            sql_query = f"""
                        SELECT
                            d.id AS department_id,
                            d.department AS department_name,
                            COUNT(*) AS num_employees_hired
                        FROM
                            employees e
                        INNER JOIN
                            departments d ON e.department_id = d.id
                        WHERE
                            e.datetime >= '{year}-01-01' AND e.datetime <= '{year}-12-31'
                        GROUP BY
                            d.id, d.department
                        HAVING
                            COUNT(*) > (
                                SELECT
                                    AVG(num_employees_hired)
                                FROM (
                                    SELECT
                                        d.id AS department_id,
                                        COUNT(*) AS num_employees_hired
                                    FROM
                                        employees e
                                    INNER JOIN
                                        departments d ON e.department_id = d.id
                                    WHERE
                                        e.datetime >= '{year}-01-01' AND e.datetime <= '{year}-12-31'
                                    GROUP BY
                                        d.id
                                ) AS subquery
                            )
                        ORDER BY
                            num_employees_hired DESC;"""
            cursor.execute(sql_query)
            results = cursor.fetchall()
            response = DepartmentsWithAboveAVGHires(
                departments_with_above_avg_hires=[
                    DepartmentWithAboveAVGHires(
                        id=row[0],
                        department=row[1],
                        hired=row[2]) for row in results
                ]).to_dict()
        return response
    except Exception as e:
        raise e
    finally:
        db_pool.putconn(connection)
