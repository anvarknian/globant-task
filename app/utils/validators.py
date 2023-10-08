from app.models.Models import Employee, Department, Job
import logging

logger = logging.getLogger(__name__)


def validate_records(records, model_type):
    validated_records = []
    validated_record = None
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
