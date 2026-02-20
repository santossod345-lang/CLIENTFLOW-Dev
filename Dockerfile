
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

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py ./
COPY app/ ./app/
COPY backend/ ./backend/
COPY alembic/ ./alembic/
COPY alembic.ini ./
COPY init_prod.py ./
COPY --from=frontend-build /build/clientflow-frontend/dist ./clientflow-frontend/dist

# Create upload directories
RUN mkdir -p /app/uploads/logos

# Expose port
EXPOSE 8000

# Health check (no curl/apt-get needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\",\"8000\")}/api/health', timeout=5).read()"

# Start server
CMD ["/bin/sh", "-c", "gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 120 --access-logfile - --error-logfile -"]
