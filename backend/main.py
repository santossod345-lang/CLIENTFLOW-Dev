# ===== PRODUCTION DEPLOYMENT =====
# Commit: d5aca92 - All fixes deployed
# Status: /ready, /status, /public/health, /docs endpoints active
# Build: v1.0.0 with PostgreSQL integration
# =================================

import logging
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

# Routers e módulos
from backend.routers import empresa, clientes, atendimentos, public, dashboard
from backend import models, database, ai_module
from backend.dependencies import require_authenticated_empresa, get_tenant_db
from backend import auth
from backend.schemas import PerguntaIA
from backend.analytics import get_date_range, build_metric_change, normalize_period


def _parse_brl_number(value) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    raw = str(value).strip()
    if not raw:
        return 0.0
    raw = raw.replace("R$", "").strip()
    raw = re.sub(r"[^0-9,\.\-]", "", raw)
    if not raw or raw == "-":
        return 0.0

    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")

    try:
        return float(raw)
    except ValueError:
        return 0.0


def _period_key(raw: Optional[str]) -> str:
    if not raw:
        return "30d"
    v = str(raw).strip().lower()
    mapping = {
        "hoje": "today",
        "today": "today",
        "7": "7d",
        "7d": "7d",
        "7dias": "7d",
        "7_days": "7d",
        "30": "30d",
        "30d": "30d",
        "30dias": "30d",
        "30_days": "30d",
        "mes": "month",
        "mês": "month",
        "month": "month",
        "mes_atual": "month",
        "current_month": "month",
    }
    return mapping.get(v, v)


def _get_period_ranges(period: str, now: datetime):
    if period == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "7d":
        start = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "30d":
        start = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "month":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)

    end = now
    duration = end - start
    prev_end = start
    prev_start = start - duration
    return start, end, prev_start, prev_end


def _comparison(current_value: float, previous_value: float):
    if previous_value == 0:
        if current_value == 0:
            pct = 0.0
        else:
            pct = 100.0
    else:
        pct = ((current_value - previous_value) / previous_value) * 100.0
    return {
        "valor_atual": current_value,
        "valor_periodo_anterior": previous_value,
        "percentual_variacao": round(pct, 1),
    }


def _date_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def _build_daily_series(start: datetime, end: datetime):
    labels = []
    cur = start.replace(hour=0, minute=0, second=0, microsecond=0)
    last = end.replace(hour=0, minute=0, second=0, microsecond=0)
    while cur <= last:
        labels.append(_date_key(cur))
        cur += timedelta(days=1)
    return labels

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("clientflow")

# Environment detection (used before app creation for CORS and lifespan)
environment = os.getenv("ENVIRONMENT", "development").lower().strip()


@asynccontextmanager
async def lifespan(application: FastAPI):
    """FastAPI lifespan handler for startup/shutdown tasks."""
    try:
        logger.info("Starting up ClientFlow API...")
        # In development with SQLite, auto-create tables (no Alembic needed)
        if database._is_sqlite:
            logger.info("SQLite detected — creating tables automatically for development")
            models.Base.metadata.create_all(bind=database.engine)
        _run_startup_migrations_if_needed()
        if os.getenv("PRINT_ROUTES", "false").lower() in {"1", "true", "yes", "on"}:
            routes_summary = []
            for route in application.routes:
                methods = sorted(getattr(route, "methods", []) or [])
                methods_label = ",".join(methods) if methods else ""
                routes_summary.append(f"{route.path} {methods_label}".strip())
            logger.info("Routes loaded: %s", routes_summary)
        logger.info("✓ Startup completed successfully")
    except Exception as e:
        logger.error(f"✗ Startup failed (non-fatal): {e}")
        # Do NOT raise - let app run even if migrations fail
        # This prevents Railway 502 errors from startup failures
    yield


# Instância FastAPI
# Version includes commit hash for deployment verification (forces Docker cache bust)
app = FastAPI(title="ClientFlow API", version="1.0.0-ca09e68-deploy-final", lifespan=lifespan)

# CORS Configuration
# - Production: allow ONLY the configured frontend origins via ALLOWED_ORIGINS
# - Development: allow configured origins + localhost (Vite/React dev servers)
raw_origins = os.getenv("ALLOWED_ORIGINS", "").strip()

if environment == "production":
    if not raw_origins or raw_origins == "*":
        # Do not crash the service for missing CORS config; default to the known Vercel domain
        # so the app can come up and be debugged. Strongly recommend setting ALLOWED_ORIGINS.
        logger.warning(
            "ALLOWED_ORIGINS is not set (or is '*') in production; using Vercel domain fallback"
        )
        raw_origins = "https://clientflow-dev-one.vercel.app,https://*.vercel.app"
else:
    # In dev, default to common local frontend ports if not specified
    if not raw_origins or raw_origins == "*":
        raw_origins = "http://localhost:3000,http://localhost:5173"

allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip()]

if environment != "production":
    allowed_origins = sorted(
        set(
            allowed_origins
            + [
                "http://localhost:3000",
                "http://localhost:5173",
                "http://127.0.0.1:3000",
                "http://127.0.0.1:5173",
            ]
        )
    )

logger.info(f"CORS allowed origins: {allowed_origins}")

allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["*"],
)

# Mount static files for logo uploads
uploads_dir = Path(os.getenv("UPLOADS_DIR", "uploads"))
uploads_dir.mkdir(parents=True, exist_ok=True)
(uploads_dir / "logos").mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


def _run_startup_migrations_if_needed() -> None:
    """Run Alembic migrations automatically on startup (production-safe).

    Uses a PostgreSQL advisory lock to avoid multiple workers running migrations concurrently.
    """

    # In production, prefer NOT to run migrations during API startup.
    # Reason: if the database is slow/unavailable/misconfigured, the app can fail to bind
    # the PORT in time and Railway returns 502/"request did not respond".
    default_flag = "false" if environment == "production" else "true"
    run_flag = os.getenv("RUN_MIGRATIONS_ON_STARTUP", default_flag).lower().strip()
    if run_flag not in {"1", "true", "yes", "on"}:
        logger.info(f"Migrations on startup disabled (RUN_MIGRATIONS_ON_STARTUP={run_flag})")
        return

    try:
        from sqlalchemy import text
        from backend.database import engine, SQLALCHEMY_DATABASE_URL
    except Exception as e:
        logger.warning(f"Skipping migrations (database not ready): {e}")
        return

    db_url = (SQLALCHEMY_DATABASE_URL or "").lower()
    if not (db_url.startswith("postgresql") or "postgresql" in db_url):
        logger.info("Skipping migrations (not PostgreSQL)")
        return

    lock_key = 827364  # stable app-specific integer

    # Hold lock on a dedicated connection while running Alembic.
    # Set short timeout to avoid blocking app startup
    
    with engine.connect() as conn:
        try:
            # Try to acquire lock with 5 second timeout
            locked = conn.execute(
                text("SELECT pg_try_advisory_lock(:k)"), 
                {"k": lock_key}
            ).scalar()
        except Exception as e:
            logger.warning(f"Could not acquire advisory lock for migrations: {e}")
            return

        if not locked:
            logger.info("Migrations already running in another worker; skipping")
            return

        try:
            from alembic import command
            from alembic.config import Config

            repo_root = Path(__file__).resolve().parents[1]
            alembic_ini = repo_root / "alembic.ini"

            cfg = Config(str(alembic_ini))
            # Make sure relative paths work regardless of CWD
            cfg.set_main_option("script_location", str(repo_root / "alembic"))
            command.upgrade(cfg, "head")
            logger.info("✓ Alembic migrations applied")
        except Exception:
            logger.exception("Alembic migrations failed")
            # Default to keeping the service up (so /api/health and logs are reachable).
            # If you prefer fail-fast in production, set FAIL_ON_MIGRATION_ERROR=true.
            fail_fast = os.getenv("FAIL_ON_MIGRATION_ERROR", "false").lower().strip() in {"1", "true", "yes", "on"}
            if environment == "production" and fail_fast:
                raise
        finally:
            # The lock is released when the connection closes, but unlock explicitly if possible.
            try:
                conn.execute(text("SELECT pg_advisory_unlock(:k)"), {"k": lock_key})
            except Exception:
                pass

# Criação das tabelas (desabilitado em produção - usar Alembic migrations)
# Em produção, execute: alembic upgrade head
# models.Base.metadata.create_all(bind=database.engine)

# ===== REGISTER ALL ROUTERS =====
app.include_router(empresa.router)
app.include_router(clientes.router)
app.include_router(atendimentos.router)
app.include_router(dashboard.router)
app.include_router(public.router)

# Serve frontend SPA only when explicitly enabled (frontend is typically deployed on Vercel)
serve_frontend = os.getenv("SERVE_FRONTEND", "false").lower() == "true"
frontend_dist = Path("clientflow-frontend/dist")
if serve_frontend and frontend_dist.exists():
    # Mount under /app to avoid shadowing API routes like /status and /docs
    app.mount("/app", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")


# ===== READINESS ENDPOINT FOR RAILWAY HEALTH CHECKS =====
@app.get("/ready")
def readiness():
    """Kubernetes/Railway-style readiness probe (no DB check)"""
    return {"ready": True, "timestamp": datetime.now().isoformat()}

# Middleware para injetar empresa_id do JWT
@app.middleware("http")
async def inject_empresa_id_jwt(request: Request, call_next):
    """Extract empresa_id from JWT and inject into request state."""
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split()[1]
        try:
            from backend.auth import jwt, SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            empresa_id = payload.get("sub")
            if empresa_id:
                request.state.empresa_id = empresa_id
        except Exception as err:
            logger.debug(f"JWT parsing failed (expected for public endpoints): {type(err).__name__}")
            # Do NOT fail - public endpoints don't need JWT
    response = await call_next(request)
    return response

# Health check endpoints
@app.get("/health")
def health():
    """Full health check with database validation"""
    try:
        from sqlalchemy import text
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "ok", "version": "1.0.0", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(status_code=503, content={"status": "error", "error": str(e)})

@app.get("/api/health")
def api_health():
    """Simple health check for load balancers (no DB check)"""
    return {"status": "ok", "version": "1.0.0"}

# Assistente IA Interno
@app.post("/ia/perguntar")
def ia_perguntar(
    body: PerguntaIA,
    token: Optional[str] = Query(None),
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
    tenant_db: Session = Depends(get_tenant_db)
):
    try:
        if token:
            payload = auth.decode_access_token(token)
            if payload:
                empresa_id = payload.get("sub")
                if empresa_id:
                    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
                    if not empresa:
                        return JSONResponse(status_code=401, content={"error": "Empresa não encontrada"})
            from sqlalchemy import text
            tenant_db.execute(text(f"SET search_path TO empresa_{empresa.id}, public"))
        clients = tenant_db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa.id).all()
        atendimentos = tenant_db.query(models.Atendimento).filter(models.Atendimento.empresa_id == empresa.id).all()
        contexto = f"Clients: {[c.nome for c in clients]}\nAtendimentos: {len(atendimentos)}"
        resposta = ai_module.responder_pergunta(body.pergunta, contexto)
        return {"resposta": resposta}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.get("/api/dashboard/analytics")
def obter_dashboard_analytics(
    period: str = Query("7d"),
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    tenant_db: Session = Depends(get_tenant_db),
):
    """Professional analytics endpoint for the premium dashboard.

    Security:
    - Requires authenticated empresa (JWT)
    - Never trusts empresa_id from the frontend

    Performance:
    - Uses aggregated SQL queries (no N+1)
    - Groups series by day
    """
    from sqlalchemy import func, case, cast
    from sqlalchemy.types import Numeric

    period_key = normalize_period(period)
    dr = get_date_range(period_key)

    dialect = tenant_db.bind.dialect.name if tenant_db.bind is not None else ""

    def revenue_expr(col):
        # Atendimento.valor_cobrado is a string; normalize to numeric at SQL-level.
        # Handles common formats:
        # - "1234.56" (decimal '.')
        # - "1.234,56" (thousands '.', decimal ',')
        # - "1234,56" (decimal ',')
        cleaned = func.regexp_replace(col, r"[^0-9,\.\-]", "", "g") if dialect == "postgresql" else col
        if dialect == "postgresql":
            has_comma = func.strpos(cleaned, ",") > 0
            normalized = case(
                (has_comma, func.replace(func.replace(cleaned, ".", ""), ",", ".")),
                else_=cleaned,
            )
            return cast(normalized, Numeric)

        # Fallback for non-Postgres dialects: try a simple replace and cast.
        normalized = func.replace(cleaned, ",", ".")
        return cast(normalized, Numeric)

    revenue_col = revenue_expr(models.Atendimento.valor_cobrado)

    # Appointments + revenue (current)
    appt_current_count, appt_current_revenue = tenant_db.query(
        func.count(models.Atendimento.id),
        func.coalesce(func.sum(revenue_col), 0),
    ).filter(
        models.Atendimento.empresa_id == empresa.id,
        models.Atendimento.data_atendimento >= dr.start_date,
        models.Atendimento.data_atendimento < dr.end_date,
    ).one()

    # Appointments + revenue (previous)
    appt_prev_count, appt_prev_revenue = tenant_db.query(
        func.count(models.Atendimento.id),
        func.coalesce(func.sum(revenue_col), 0),
    ).filter(
        models.Atendimento.empresa_id == empresa.id,
        models.Atendimento.data_atendimento >= dr.start_date_previous,
        models.Atendimento.data_atendimento < dr.end_date_previous,
    ).one()

    # New clients (current/previous)
    clients_current = tenant_db.query(func.count(models.Cliente.id)).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.data_primeiro_contato >= dr.start_date,
        models.Cliente.data_primeiro_contato < dr.end_date,
    ).scalar() or 0

    clients_previous = tenant_db.query(func.count(models.Cliente.id)).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.data_primeiro_contato >= dr.start_date_previous,
        models.Cliente.data_primeiro_contato < dr.end_date_previous,
    ).scalar() or 0

    # Revenue series by day
    appt_date = func.date(models.Atendimento.data_atendimento)
    revenue_series_rows = (
        tenant_db.query(
            appt_date.label("date"),
            func.coalesce(func.sum(revenue_col), 0).label("value"),
        )
        .filter(
            models.Atendimento.empresa_id == empresa.id,
            models.Atendimento.data_atendimento >= dr.start_date,
            models.Atendimento.data_atendimento < dr.end_date,
        )
        .group_by(appt_date)
        .order_by(appt_date)
        .all()
    )

    revenue_series = [
        {
            "date": (r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date)),
            "value": float(r.value or 0),
        }
        for r in revenue_series_rows
    ]

    # New clients series by day
    client_date = func.date(models.Cliente.data_primeiro_contato)
    clients_series_rows = (
        tenant_db.query(
            client_date.label("date"),
            func.count(models.Cliente.id).label("value"),
        )
        .filter(
            models.Cliente.empresa_id == empresa.id,
            models.Cliente.data_primeiro_contato >= dr.start_date,
            models.Cliente.data_primeiro_contato < dr.end_date,
        )
        .group_by(client_date)
        .order_by(client_date)
        .all()
    )

    clients_series = [
        {
            "date": (r.date.isoformat() if hasattr(r.date, "isoformat") else str(r.date)),
            "value": int(r.value or 0),
        }
        for r in clients_series_rows
    ]

    return {
        "metrics": {
            "revenue": build_metric_change(float(appt_current_revenue or 0), float(appt_prev_revenue or 0)),
            "clients": build_metric_change(float(clients_current), float(clients_previous)),
            "appointments": build_metric_change(float(appt_current_count), float(appt_prev_count)),
        },
        "revenue_series": revenue_series,
        "clients_series": clients_series,
    }

# Rota raiz
@app.get("/")
def root():
    return {
        "message": "ClientFlow API v1.0.0",
        "status": "online",
        "docs": "/docs",
        "timestamps": {
            "server_start": datetime.now().isoformat()
        }
    }

# Root status endpoint - for health checks/monitoring
@app.get("/status")
def status():
    """Server readiness status. Used by Railway health checks."""
    try:
        from sqlalchemy import text
        with database.engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.warning(f"Status check - DB connection issue: {e}")
        return {
            "status": "degraded",
            "database": "unavailable",
            "version": "1.0.0"
        }

# Execução local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
