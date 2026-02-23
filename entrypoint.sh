#!/bin/bash
set -e

echo "🚀 ClientFlow API - Starting entrypoint..."
echo "Port: ${PORT:-8000}"
echo "Workers: ${WORKERS:-4}"
echo "Timeout: ${TIMEOUT:-120}"

# Ensure app can import
python -c "from backend.main import app; print('✓ App module OK'); print('✓ Routes:', len(app.routes))" || exit 1

# Start Gunicorn with explicit configuration
exec gunicorn \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers ${WORKERS:-4} \
    --worker-class uvicorn.workers.UvicornWorker \
    --timeout ${TIMEOUT:-120} \
    --access-logfile - \
    --error-logfile - \
    --log-level debug \
    backend.main:app
