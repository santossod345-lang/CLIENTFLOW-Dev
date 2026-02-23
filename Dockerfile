# Railway sync marker: 2026-02-23-deploy-96eab76
# Build Date: 2026-02-23T05:47:00Z
# Force rebuild: CACHEBUST=2026-02-23T05:47:00Z-PROCFILE-TEST
ARG CACHEBUST=2026-02-23T05:47:00Z-PROCFILE-TEST
FROM node:18-alpine AS frontend-build

WORKDIR /build

COPY clientflow-frontend/package.json clientflow-frontend/package-lock.json ./clientflow-frontend/
RUN cd clientflow-frontend && npm ci

COPY clientflow-frontend/ ./clientflow-frontend/

# Use same-origin API by default; VITE_API_URL can be overridden at build time.
ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

RUN cd clientflow-frontend && npm run build

FROM python:3.11-slim

WORKDIR /app

# Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies for PostgreSQL
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY entrypoint.sh ./
RUN chmod +x ./entrypoint.sh
COPY --from=frontend-build /build/clientflow-frontend/dist ./clientflow-frontend/dist

# Create upload directories
RUN mkdir -p /app/uploads/logos

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\",\"8000\")}/ready', timeout=5).read()"

# Procfile will handle startup on Railway; entrypoint.sh is the entry point
# CMD intentionally omitted to let Railway use Procfile
