# Use an official Python runtime as a parent image
FROM python:3.9 AS dev

# Set environment variables
ENV PYTHONUNBUFFERED 1
ENV PRISMA_PY_DEBUG=0

WORKDIR /globant-task

COPY requirements.txt /globant-task
COPY schema.prisma /globant-task/schema.prisma


FROM dev AS prod

RUN pip install -r requirements.txt