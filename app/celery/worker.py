import logging

from celery import Celery

from app.celery.db import DatabaseConnection
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.models.Models import EmployeeCountByQuarter, EmployeesCountByQuarter, \
    DepartmentsWithAboveAVGHires, DepartmentWithAboveAVGHires
from app.utils.queries import return_query_1, return_query_2, insert_records_query
from app.utils.readers import read_csv
from app.utils.validators import validate_records

logger = logging.getLogger(__name__)

celery = Celery(__name__)

celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND

db = DatabaseConnection()
db_connection = db.conn


def insert_records(records, table_name, model_fields):
    cursor = None
    batch_size = 1000
    records_to_insert = [tuple(record) for record in records]
    total_received = len(records_to_insert)
    total_inserted = 0
    total_skipped = 0

    try:
        db.check_connection()
        cursor = db_connection.cursor()
        placeholders = ', '.join(['%s'] * len(model_fields))
        columns = ', '.join(model_fields)

        for i in range(0, len(records_to_insert), batch_size):
            batch_data = records_to_insert[i:i + batch_size]

            query = (insert_records_query(table_name, columns, placeholders))
            cursor.executemany(query, batch_data)
            db_connection.commit()

            inserted = cursor.rowcount
            skipped = len(batch_data) - inserted
            total_inserted += inserted
            total_skipped += skipped

        return total_received, total_inserted, total_skipped
    except Exception as e:
        db_connection.rollback()
        logger.error("Error insert_records: %s", str(e))
        raise e
    finally:
        if cursor:
            cursor.close()
        logger.info("Finished insert_records")


def process_csv_file(file_name, model_type):
    full_file_path = f"data/{model_type}/{file_name}"

    csv_data = read_csv(full_file_path)
    if len(csv_data) == 0:
        return

    try:
        records = [row for row in csv_data]
        validated_records = validate_records(records, model_type)
        data = [list(record.dict().values()) for record in validated_records]
        return data, len(records), len(data)
    except Exception as e:
        logger.error("Error insert_data_from_csv: %s", str(e))
        raise e
    finally:
        logger.info("Finished insert_data_from_csv")


@celery.task(name="insert_records_task")
def insert_records_task(file_name, table_name):
    model_fields = None
    tables = ['employees', 'jobs', 'departments']

    if table_name == "jobs":
        model_fields = ["id", "job"]

    if table_name == "departments":
        model_fields = ["id", "department"]

    if table_name == "employees":
        model_fields = ["id", "name", "datetime", "department_id", "job_id"]

    if table_name not in tables or model_fields is None:
        raise ValueError(f"Invalid model_type - {table_name}")

    try:
        data, total_received, total_validated = process_csv_file(file_name, table_name)
        total_received_insert, total_inserted, total_skipped = insert_records(data, table_name, model_fields)

        return {
            "Total Received": total_received,
            "Total Validated": total_validated,
            "Total Validation Ignored": total_received - total_validated,
            "Total Received For Insert": total_received_insert,
            "Total Inserted": total_inserted,
            "Total Insert Skipped": total_skipped,
        }
    except Exception as e:
        logger.error("Error in insert_records_task: %s", str(e))
        raise e
    finally:
        logger.info("Finished insert_records_task")


@celery.task(name="get_analytics_task")
def get_analytics_task(year: int, query: int):
    cursor, response = None, None
    try:
        db.check_connection()
        cursor = db_connection.cursor()
        if query == 1:
            sql_query = return_query_1(year)
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
            sql_query = return_query_2(year)
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
        logger.error("Error in get_analytics_task: %s", str(e))
        raise e
    finally:
        if cursor:
            cursor.close()
        logger.info("Finished get_analytics_task")
