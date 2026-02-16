Backend Professionalization - ClientFlow

Overview:
- This module contains the FastAPI backend. The repository was extended with a professional authentication flow (access + refresh tokens), refresh token rotation and revocation, and initial multi-tenant support via per-tenant schemas.

Required environment variables (add to CI/GitHub Secrets or runtime env):
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`
- `JWT_SECRET_KEY` (strong secret, required for stable JWTs)
- `JWT_ALGORITHM` (default HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES` (default 15)
- `REFRESH_TOKEN_EXPIRE_DAYS` (default 7)

Notes:
- The code adds `RefreshToken` model. After updating code, run database migrations or recreate schema for dev.
- The implementation keeps compatibility with the previous session token mechanism (`active_sessions`) while exposing new `access_token` and `refresh_token` in login responses.
- There is a basic in-memory rate limiter on login for immediate protection; replace with Redis rate-limiter when scaling.

Database migrations (Alembic)
1. Configure your database connection via environment variables used in `backend/database.py` (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`, `POSTGRES_PORT`).
2. Install Alembic if not present: `pip install alembic`
3. To run migrations locally (run from repository root):

```bash
# ensure env vars set (example)
export POSTGRES_USER=clientflow
export POSTGRES_PASSWORD=clientflow
export POSTGRES_DB=clientflow
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

# run alembic upgrade
alembic upgrade head
```

4. A helper script is provided at `scripts/run_migrations.sh` to validate env vars and run `alembic upgrade head`.

