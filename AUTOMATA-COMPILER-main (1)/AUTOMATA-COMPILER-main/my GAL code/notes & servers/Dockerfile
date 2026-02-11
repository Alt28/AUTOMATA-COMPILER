# syntax=docker/dockerfile:1
# Simple production-ready container for the Grow A Language web app

FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Install build essentials only if needed (commented out for now)
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

# Copy dependency spec first for caching
COPY requirements.txt ./
RUN python -m venv .venv \
    && .venv/bin/pip install --upgrade pip \
    && .venv/bin/pip install -r requirements.txt

# Copy application code
COPY . .

# Expose port (default 5000)
EXPOSE 5000

# Environment configuration (override at runtime)
ENV HOST=0.0.0.0 \
    PORT=5000 \
    DEBUG=false

# Use eventlet for production Socket.IO (if included in requirements)
CMD ["python", "server.py"]
