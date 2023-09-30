# globant-task

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

