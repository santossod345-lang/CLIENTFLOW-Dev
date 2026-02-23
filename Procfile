web: /bin/sh -c "exec gunicorn backend.main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers 1 --timeout 60 --access-logfile - --error-logfile -"
