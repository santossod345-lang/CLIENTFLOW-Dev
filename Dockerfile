
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

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

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
COPY generate_secrets.py ./
COPY --from=frontend-build /build/clientflow-frontend/dist ./clientflow-frontend/dist

# Create upload directories
RUN mkdir -p /app/uploads/logos

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /bin/sh -c "curl -f http://localhost:${PORT:-8000}/api/health || exit 1"

# Start server
CMD ["/bin/sh", "-c", "gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers 2 --timeout 120 --access-logfile - --error-logfile -"]
