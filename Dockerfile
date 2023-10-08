FROM python:3.9 AS dev

ENV PYTHONUNBUFFERED=0
ENV PRISMA_PY_DEBUG=0

WORKDIR /globant-task

COPY requirements.txt /globant-task
COPY schema.prisma /globant-task/schema.prisma
COPY .env /globant-task/.env

FROM dev AS prod
RUN pip install -r requirements.txt