import csv
import logging
import os

from celery import Celery, states
from psycopg2 import pool

from app.models.Models import Employee, Department, Job

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize a connection pool
db_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    database="globant",
    user="postgres",
    password="postgres",
    host="postgres",
    port="5432"
)

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")


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
    try:
        cursor = connection.cursor()
        placeholders = ', '.join(['%s'] * len(model_fields))
        columns = ', '.join(model_fields)
        records_to_insert = [tuple(record) for record in records]
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.executemany(query, records_to_insert)
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

        # Validate records
        validated_records = validate_records(records, model_type)

        # Extract data from validated records
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
