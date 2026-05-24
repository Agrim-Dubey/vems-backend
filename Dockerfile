# Dockerfile

FROM python:3.12-alpine

# Prevents python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevents python buffering
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apk update && apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    postgresql-dev \
    jpeg-dev \
    zlib-dev \
    cargo \
    bash

# Install dependencies
COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt
RUN apk add --no-cache netcat-openbsd

# Copy project
COPY . .

# Entrypoint
RUN chmod +x /app/docker/entrypoint.sh

ENTRYPOINT ["/app/docker/entrypoint.sh"]