
import logging
from fastapi import FastAPI, Request, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

# Routers e módulos
from backend.routers import empresa, clientes, dashboard
from backend import models, database, ai_module
from backend.dependencies import require_authenticated_empresa, get_tenant_db
from backend import auth
from backend.schemas import PerguntaIA

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger("clientflow")

# Instância FastAPI
app = FastAPI(title="ClientFlow API", version="1.0.0")

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criação das tabelas
models.Base.metadata.create_all(bind=database.engine)

# Registrar routers
app.include_router(empresa.router)
app.include_router(clientes.router)
app.include_router(dashboard.router)

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

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

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

    return {
        "empresa": {
            "nome": empresa.nome_empresa,
            "nicho": empresa.nicho
        },
        "estatisticas": {
            "total_clientes": total_clientes,
            "total_atendimentos": total_atendimentos,
            "tempo_medio_retorno": tempo_medio_retorno,
            "clientes_novos_mes": clientes_novos_mes
        },
        "atendimentos_recentes": atendimentos_recentes,
        "top_clientes": top_clientes
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
