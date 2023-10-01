# globant-task

#### DB Diagram:

![Alt text](static/schema.svg)

#### Application Architecture:

![Alt text](static/architecture.svg)

run with Docker:

```bash
docker compose up -d
```

API Available at:

```agsl
http://localhost:8080/docs#/
OR
http://localhost:8080/redoc
```

Scale the worker instances:

```bash
docker compose up -d --scale worker=3
```

Monitor the logs:

```agsl
http://localhost:5555/dashboard
```

Send jobs to the API:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/jobs/file/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@jobs.csv;type=text/csv'
```

Send departments to the API:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/departments/file/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@departments.csv;type=text/csv'
```

Send employees to the API:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/employees/file/' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@employees.csv;type=text/csv'
```

Get all jobs:

```bash
curl -X 'GET' \
  'http://localhost:8080/api/jobs/' \
  -H 'accept: application/json'
```

Get all departments:

```bash
curl -X 'GET' \
  'http://localhost:8080/api/departments/' \
  -H 'accept: application/json'
```

Get all employees:

```bash
curl -X 'GET' \
  'http://localhost:8080/api/employees/' \
  -H 'accept: application/json'
```

Post new Job:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/jobs/job' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": 0,
  "job": "Test Job"
}'
```

Post new Department:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/departments/department' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": 0,
  "department": "Test Department
}'
```

post new Employee:

```bash
curl -X 'POST' \
  'http://localhost:8080/api/employees/employee' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "id": 0,
  "name": "Test Employee",
  "job": 0,
  "department_id": 0
  }'
```


