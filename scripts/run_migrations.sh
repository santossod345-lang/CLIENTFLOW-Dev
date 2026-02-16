#!/usr/bin/env bash
set -euo pipefail

echo "Running Alembic migrations (upgrade head)"

REQUIRED_VARS=(POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB POSTGRES_HOST POSTGRES_PORT)
for v in "${REQUIRED_VARS[@]}"; do
  if [ -z "${!v:-}" ]; then
    echo "Environment variable $v is not set. Aborting."
    exit 1
  fi
done

if ! command -v alembic >/dev/null 2>&1; then
  echo "alembic not found in PATH. Install with: pip install alembic"
  exit 1
fi

echo "Environment variables check passed. Executing: alembic upgrade head"
alembic upgrade head

echo "Migrations applied."
