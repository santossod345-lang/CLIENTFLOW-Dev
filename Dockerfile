# ClientFlow Backend — Railway deployment
# Frontend is deployed separately on Vercel (clientflow-frontend/)
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

# Create upload directories
RUN mkdir -p /app/uploads/logos

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\",\"8000\")}/ready', timeout=5).read()"

CMD exec gunicorn --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 60 --worker-class uvicorn.workers.UvicornWorker --access-logfile - --error-logfile - backend.main:app
