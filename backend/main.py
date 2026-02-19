
import logging
import os
import re
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta

# Routers e módulos
from backend.routers import empresa, clientes
from backend.routers import atendimentos
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

# Instância FastAPI
app = FastAPI(title="ClientFlow API", version="1.0.0")

# CORS Configuration
# - Production: allow ONLY the configured frontend origins via ALLOWED_ORIGINS
# - Development: allow configured origins + localhost (Vite/React dev servers)
environment = os.getenv("ENVIRONMENT", "development").lower().strip()
raw_origins = os.getenv("ALLOWED_ORIGINS", "").strip()

if environment == "production":
    if not raw_origins or raw_origins == "*":
        # Do not crash the service for missing CORS config; default to the known Vercel domain
        # so the app can come up and be debugged. Strongly recommend setting ALLOWED_ORIGINS.
        logger.warning(
            "ALLOWED_ORIGINS is not set (or is '*') in production; defaulting to https://clientflow-dev-one.vercel.app"
        )
        raw_origins = "https://clientflow-dev-one.vercel.app"
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

allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
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

    run_flag = os.getenv("RUN_MIGRATIONS_ON_STARTUP", "true").lower().strip()
    if run_flag not in {"1", "true", "yes", "on"}:
        return

    try:
        from sqlalchemy import text
        from backend.database import engine, SQLALCHEMY_DATABASE_URL
    except Exception as e:
        logger.warning(f"Skipping migrations (database not ready): {e}")
        return

    db_url = (SQLALCHEMY_DATABASE_URL or "").lower()
    if not (db_url.startswith("postgresql") or "postgresql" in db_url):
        return

    lock_key = 827364  # stable app-specific integer

    # Hold lock on a dedicated connection while running Alembic.
    with engine.connect() as conn:
        try:
            locked = conn.execute(text("SELECT pg_try_advisory_lock(:k)"), {"k": lock_key}).scalar()
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

# Registrar routers
app.include_router(empresa.router)
app.include_router(clientes.router)


@app.on_event("startup")
def _startup_tasks():
    _run_startup_migrations_if_needed()
app.include_router(atendimentos.router)

# Serve frontend SPA only when explicitly enabled (frontend is typically deployed on Vercel)
serve_frontend = os.getenv("SERVE_FRONTEND", "false").lower() == "true"
frontend_dist = Path("clientflow-frontend/dist")
if serve_frontend and frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

# Middleware para injetar empresa_id do JWT
@app.middleware("http")
async def inject_empresa_id_jwt(request: Request, call_next):
    auth_header = request.headers.get("authorization")
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split()[1]
        try:
            from backend.auth import jwt, SECRET_KEY, ALGORITHM
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            empresa_id = payload.get("sub")
            if empresa_id:
                request.state.empresa_id = empresa_id
        except Exception:
            pass
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

# Rota de dashboard
@app.get("/api/dashboard")
def obter_dashboard(
    token: Optional[str] = Query(None),
    period: Optional[str] = Query(None),
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
    tenant_db: Session = Depends(get_tenant_db)
):
    """
    Retorna estatísticas do dashboard (isolated by empresa)
    """
    if token:
        payload = auth.decode_access_token(token)
        if payload:
            empresa_id = payload.get("sub")
            if empresa_id:
                empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
                if not empresa:
                    return {"error": "Empresa não encontrada"}
        from sqlalchemy import text
        tenant_db.execute(text(f"SET search_path TO empresa_{empresa.id}, public"))

    total_clientes = tenant_db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id
    ).count()

    total_atendimentos = tenant_db.query(models.Atendimento).filter(
        models.Atendimento.empresa_id == empresa.id
    ).count()

    total_clientes_ativos = tenant_db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.inativo == 0
    ).count()
    total_clientes_inativos = tenant_db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.inativo == 1
    ).count()

    # Últimos 5 atendimentos
    ultimos_atendimentos = tenant_db.query(
        models.Atendimento,
        models.Cliente.nome.label("cliente_nome")
    ).join(
        models.Cliente, models.Atendimento.cliente_id == models.Cliente.id
    ).filter(
        models.Atendimento.empresa_id == empresa.id
    ).order_by(models.Atendimento.data_atendimento.desc()).limit(5).all()

    atendimentos_recentes = []
    for atendimento, cliente_nome in ultimos_atendimentos:
        atendimentos_recentes.append({
            "id": atendimento.id,
            "cliente_nome": cliente_nome,
            "tipo_servico": atendimento.tipo_servico,
            "data": atendimento.data_atendimento.strftime("%d/%m/%Y %H:%M") if atendimento.data_atendimento else None
        })

    # Top 5 clients mais ativos (com mais atendimentos)
    from sqlalchemy import func, asc
    top_clientes_query = (
        tenant_db.query(
            models.Cliente.id,
            models.Cliente.nome,
            func.count(models.Atendimento.id).label("total_atendimentos")
        )
        .join(models.Atendimento, models.Cliente.id == models.Atendimento.cliente_id)
        .filter(models.Cliente.empresa_id == empresa.id)
        .group_by(models.Cliente.id, models.Cliente.nome)
        .order_by(func.count(models.Atendimento.id).desc())
        .limit(5)
        .all()
    )
    top_clientes = [
        {
            "id": c.id,
            "nome": c.nome,
            "total_atendimentos": c.total_atendimentos
        }
        for c in top_clientes_query
    ]

    # Calcular tempo médio de retorno (dias entre atendimentos do mesmo cliente)
    intervalos = []
    clientes_ids = tenant_db.query(models.Cliente.id).filter(models.Cliente.empresa_id == empresa.id).all()
    for (cid,) in clientes_ids:
        atendimentos = tenant_db.query(models.Atendimento).filter(
            models.Atendimento.cliente_id == cid
        ).order_by(asc(models.Atendimento.data_atendimento)).all()
        datas = [a.data_atendimento for a in atendimentos if a.data_atendimento]
        if len(datas) > 1:
            for i in range(1, len(datas)):
                diff = (datas[i] - datas[i-1]).days
                if diff > 0:
                    intervalos.append(diff)

    tempo_medio_retorno = round(sum(intervalos)/len(intervalos), 1) if intervalos else None

    # Clientes novos do mês
    hoje = datetime.today()
    inicio_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    clientes_novos_mes = tenant_db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.data_primeiro_contato >= inicio_mes
    ).count()

    # Premium: métricas por período + comparação com período anterior
    now = datetime.today()
    period_key = _period_key(period)
    p_start, p_end, prev_start, prev_end = _get_period_ranges(period_key, now)

    atendimentos_periodo = tenant_db.query(
        models.Atendimento.data_atendimento,
        models.Atendimento.valor_cobrado,
    ).filter(
        models.Atendimento.empresa_id == empresa.id,
        models.Atendimento.data_atendimento >= p_start,
        models.Atendimento.data_atendimento < p_end
    ).all()
    atendimentos_prev = tenant_db.query(
        models.Atendimento.data_atendimento,
        models.Atendimento.valor_cobrado,
    ).filter(
        models.Atendimento.empresa_id == empresa.id,
        models.Atendimento.data_atendimento >= prev_start,
        models.Atendimento.data_atendimento < prev_end
    ).all()

    receita_atual = sum(_parse_brl_number(valor) for _, valor in atendimentos_periodo)
    receita_anterior = sum(_parse_brl_number(valor) for _, valor in atendimentos_prev)

    clientes_novos_periodo = tenant_db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.data_primeiro_contato >= p_start,
        models.Cliente.data_primeiro_contato < p_end
    ).count()
    clientes_novos_prev = tenant_db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.data_primeiro_contato >= prev_start,
        models.Cliente.data_primeiro_contato < prev_end
    ).count()

    atendimentos_count_atual = len(atendimentos_periodo)
    atendimentos_count_anterior = len(atendimentos_prev)

    labels = _build_daily_series(p_start, p_end)
    receita_por_dia = {k: 0.0 for k in labels}
    for dt, valor in atendimentos_periodo:
        if not dt:
            continue
        key = _date_key(dt)
        if key in receita_por_dia:
            receita_por_dia[key] += _parse_brl_number(valor)

    novos_clientes_por_dia = {k: 0 for k in labels}
    clientes_periodo_datas = tenant_db.query(models.Cliente.data_primeiro_contato).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.data_primeiro_contato >= p_start,
        models.Cliente.data_primeiro_contato < p_end
    ).all()
    for (dt,) in clientes_periodo_datas:
        if not dt:
            continue
        key = _date_key(dt)
        if key in novos_clientes_por_dia:
            novos_clientes_por_dia[key] += 1

    return {
        "empresa": {
            "nome": empresa.nome_empresa,
            "nicho": empresa.nicho
        },
        "estatisticas": {
            "total_clientes": total_clientes,
            "total_atendimentos": total_atendimentos,
            "total_clientes_ativos": total_clientes_ativos,
            "total_clientes_inativos": total_clientes_inativos,
            "tempo_medio_retorno": tempo_medio_retorno,
            "clientes_novos_mes": clientes_novos_mes
        },
        "atendimentos_recentes": atendimentos_recentes,
        "top_clientes": top_clientes,
        "periodo": {
            "chave": period_key,
            "inicio": p_start.isoformat(),
            "fim": p_end.isoformat(),
            "inicio_periodo_anterior": prev_start.isoformat(),
            "fim_periodo_anterior": prev_end.isoformat(),
        },
        "comparacoes": {
            "receita": _comparison(receita_atual, receita_anterior),
            "atendimentos": _comparison(float(atendimentos_count_atual), float(atendimentos_count_anterior)),
            "novos_clientes": _comparison(float(clientes_novos_periodo), float(clientes_novos_prev)),
        },
        "series": {
            "receita_diaria": {
                "labels": labels,
                "data": [round(receita_por_dia[k], 2) for k in labels],
            },
            "novos_clientes_diario": {
                "labels": labels,
                "data": [novos_clientes_por_dia[k] for k in labels],
            },
        },
    }


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
        "docs": "/docs"
    }

# Execução local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
