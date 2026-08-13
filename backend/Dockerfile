# Base stage for shared dependencies and configuration
FROM python:3.12-slim-bookworm AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy packaging configuration files first to cache dependencies
COPY pyproject.toml /app/

# Install python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .

# Development stage
FROM base AS development
ENV ENV=development
ENV PYTHONUNBUFFERED=1
# Install development/test dependencies
RUN pip install --no-cache-dir ".[dev]"
# Run dev server with reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


# Production stage
FROM base AS production
ENV ENV=production
ENV PYTHONUNBUFFERED=1

# Copy application code
COPY app/ /app/app/
COPY alembic.ini /app/
COPY alembic/ /app/alembic/

# Run production server without reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
