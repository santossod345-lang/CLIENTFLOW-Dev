"""
ClientFlow API - Enterprise-Grade SaaS Platform
A complete multi-tenant CRM and service management system
"""

import logging
from pathlib import Path
from fastapi import FastAPI, Request, Depends, Query, status
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

# Core configurations and utilities
from backend.core.config import settings
from backend.middleware import ErrorHandlingMiddleware, RequestContextMiddleware
from backend.utils import get_logger, log_action, log_error
from backend.responses import success_response, error_response
from backend.exceptions import NotFoundError

# Routers e módulos
from backend.routers import empresa, clientes, dashboard, subscriptions
from backend import models, database, ai_module
from backend.dependencies import require_authenticated_empresa, get_tenant_db
from backend import auth
from backend.schemas import PerguntaIA

# FASE 3: Segurança avançada
from backend.security import rate_limit_check, SecurityHeaders

# FASE 4: Performance
from backend.performance import cache, monitor, PaginationOptimizer

# FASE 5: Monetização SaaS
from backend.monetization import FeatureGate, PlanTier, PLANS

# Get logger
logger = get_logger("clientflow.main")

# Instância FastAPI com configurações profissionais
app = FastAPI(
    title=settings.APP_NAME,
    description="Complete multi-tenant SaaS platform for managing clients and services",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ========== MIDDLEWARES ==========

# Middleware CORS - Enterprise grade (MUST be added first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if not settings.DEBUG else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    allow_origin_regex=r"http://localhost:.*" if settings.DEBUG else None,
)

# FASE 3: Security - Rate limiting and headers
@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Middleware para aplicar rate limiting e headers de segurança"""
    try:
        await rate_limit_check(request)
    except Exception as e:
        return JSONResponse(status_code=429, content={"error": "Too many requests"})
    
    response = await call_next(request)
    # Add security headers
    for header, value in SecurityHeaders.get_security_headers().items():
        response.headers[header] = value
    return response

# ========== API ROUTERS ==========

# Registrar routers (já possuem prefixo /api completo)
app.include_router(
    empresa.router,
    tags=["Autenticação"]
)
app.include_router(
    clientes.router,
    tags=["Clientes"]
)
app.include_router(
    dashboard.router,
    tags=["Dashboard"]
)

# FASE 5: Router de subscriptions/monetização
app.include_router(
    subscriptions.router,
    tags=["Subscriptions & Billing"]
)

# ========== FRONTEND STATIC FILES ==========

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="frontend_static")

    @app.get("/", include_in_schema=False)
    def serve_root():
        return FileResponse(str(frontend_dir / "login.html"))

    @app.get("/login.html", include_in_schema=False)
    def serve_login():
        return FileResponse(str(frontend_dir / "login.html"))

    @app.get("/dashboard.html", include_in_schema=False)
    def serve_dashboard():
        return FileResponse(str(frontend_dir / "dashboard.html"))

# ========== UPLOADS (LOGOS E DEMAIS ARQUIVOS) ==========

uploads_dir = Path(__file__).resolve().parent.parent / "uploads"
uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# ========== HEALTH CHECK ==========

@app.get("/health", tags=["Health"])
def health_check():
    """
    Application health check endpoint
    
    Returns:
        dict: Status of the application
    """
    try:
        db = next(database.get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        return success_response(
            data={"status": "healthy", "version": settings.APP_VERSION},
            message="API is running"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=error_response(
                code="SERVICE_UNAVAILABLE",
                message="Database connection failed"
            )
        )


@app.get("/api/health", tags=["Health"])
def api_health_check():
    """
    API health check endpoint for load balancers
    
    Returns:
        dict: Status of the application
    """
    try:
        db = next(database.get_db())
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db.close()
        return {"status": "ok", "version": settings.APP_VERSION}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "error", "message": "Database connection failed"}
        )


# ========== ROOT ENDPOINT ==========

@app.get("/", tags=["Info"])
def root():
    """
    Root endpoint - API information
    
    Returns basic information about the API
    """
    return success_response(
        data={
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs_url": "/docs",
            "redoc_url": "/redoc"
        },
        message="ClientFlow API is online"
    )


# ========== IA ASSISTANT (Optional Feature) ==========

@app.post("/ia/ask", tags=["AI Assistant"])
def ia_ask(
    body: PerguntaIA,
    token: Optional[str] = Query(None),
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
    tenant_db: Session = Depends(get_tenant_db)
):
    """
    AI Assistant endpoint - Ask questions about your business
    
    This endpoint is optional and depends on ENABLE_AI_ASSISTANT setting
    """
    if not settings.ENABLE_AI_ASSISTANT:
        raise NotFoundError("AI Assistant")
    
    try:
        if token:
            payload = auth.decode_access_token(token)
            if payload:
                empresa_id = payload.get("sub")
                if empresa_id:
                    empresa = db.query(models.Empresa).filter(
                        models.Empresa.id == empresa_id
                    ).first()
                    if not empresa:
                        raise NotFoundError("Empresa", empresa_id)
            
            from sqlalchemy import text
            tenant_db.execute(text(f"SET search_path TO empresa_{empresa.id}, public"))
        
        clients = tenant_db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        ).all()
        atendimentos = tenant_db.query(models.Atendimento).filter(
            models.Atendimento.empresa_id == empresa.id
        ).all()
        
        contexto = f"Clients: {[c.nome for c in clients]}\nAtendimentos: {len(atendimentos)}"
        resposta = ai_module.responder_pergunta(body.pergunta, contexto)
        
        log_action(
            "ia_ask",
            "pergunta",
            usuario_id=empresa.id,
            details={"pergunta": body.pergunta[:50]}
        )
        
        return success_response(
            data={"resposta": resposta},
            message="Pergunta respondida"
        )
    except Exception as e:
        log_error(e, context="IA Assistant", user_id=empresa.id)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response(
                code="AI_ERROR",
                message="Erro ao processar pergunta"
            )
        )



# ========== EXECUTION ==========

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.APP_NAME} API v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )

