# ========== IMPORTS E DEFINIÇÕES ÚNICOS =====

# ===== IMPORTS E DEFINIÇÕES ÚNICOS =====
from fastapi import FastAPI, Body, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import ai_module
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import models
import database
import services
from models import LogAcao
import auth

app = FastAPI(title="ClientFlow API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
models.Base.metadata.create_all(bind=database.engine)
active_sessions = {}  # {token: empresa_id}

# ========== FUNÇÃO DE SESSÃO ========== 
def get_current_empresa(token: str, db: Session = Depends(database.get_db)) -> models.Empresa:
    if token not in active_sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Sessão inválida ou expirada")
    empresa_id = active_sessions[token]
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Empresa não encontrada")
    return empresa

# ========== ENDPOINTS PRINCIPAIS ========== 

from fastapi.encoders import jsonable_encoder
# ========== ENDPOINTS DE CLIENTES ========== 
class ClienteOut(BaseModel):
    id: int
    nome: str
    telefone: str
    anotacoes_rapidas: str = ""
    data_primeiro_contato: datetime
    class Config:
        orm_mode = True

@app.get("/api/clientes", response_model=List[ClienteOut])
def listar_clientes(
    token: str = Query(...),
    db: Session = Depends(database.get_db)
):
    empresa = get_current_empresa(token, db)
    clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa.id).order_by(models.Cliente.data_primeiro_contato.desc()).all()
    return clientes
from fastapi import Request

class ClienteCreate(BaseModel):
    nome: str
    telefone: str
    anotacoes_rapidas: str = ""

@app.post("/api/clientes", status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente: ClienteCreate,
    token: str = Query(...),
    db: Session = Depends(database.get_db)
):
    empresa = get_current_empresa(token, db)
    # Verifica duplicidade por telefone para a empresa
    existente = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.telefone == cliente.telefone
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Cliente já cadastrado com este telefone.")
    novo_cliente = models.Cliente(
        empresa_id=empresa.id,
        nome=cliente.nome,
        telefone=cliente.telefone,
        anotacoes_rapidas=cliente.anotacoes_rapidas
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return {
        "id": novo_cliente.id,
        "nome": novo_cliente.nome,
        "telefone": novo_cliente.telefone,
        "anotacoes_rapidas": novo_cliente.anotacoes_rapidas,
        "data_primeiro_contato": novo_cliente.data_primeiro_contato
    }

@app.post("/api/empresas/cadastrar", response_model=models.Empresa, status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(empresa: services.EmpresaCreate, db: Session = Depends(database.get_db)):
    existing = db.query(models.Empresa).filter(models.Empresa.email_login == empresa.email_login).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email já cadastrado")
    senha_hash = auth.get_password_hash(empresa.senha)
    nova_empresa = models.Empresa(
        nome_empresa=empresa.nome_empresa,
        nicho=empresa.nicho,
        telefone=empresa.telefone,
        email_login=empresa.email_login,
        senha_hash=senha_hash
    )
    db.add(nova_empresa)
    db.commit()
    db.refresh(nova_empresa)
    return nova_empresa

@app.post("/api/empresas/login")
def login_empresa(login: services.EmpresaLogin, db: Session = Depends(database.get_db)):
    empresa = db.query(models.Empresa).filter(models.Empresa.email_login == login.email_login).first()
    if not empresa or not auth.verify_password(login.senha, empresa.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
    token = auth.create_session_token()
    active_sessions[token] = empresa.id
    return {
        "token": token,
        "empresa": {
            "id": empresa.id,
            "nome_empresa": empresa.nome_empresa,
            "nicho": empresa.nicho,
            "email_login": empresa.email_login
        }
    }

@app.post("/api/empresas/logout")
def logout_empresa(token: str):
    if token in active_sessions:
        del active_sessions[token]
    return {"message": "Logout realizado com sucesso"}


# ================= IA MODULE ROUTES =================
# 2. IA Geradora de Resumos
@app.get("/ia/resumo_cliente/{cliente_id}")
def ia_resumo_cliente(cliente_id: int):
    try:
        # Função utilitária para buscar atendimentos do cliente
        from database import SessionLocal
        db = SessionLocal()
        atendimentos = db.query(models.Atendimento).filter(models.Atendimento.cliente_id == cliente_id).all()
        # Converter para lista de dicts
        atendimentos_dict = [
            {"data": a.data_atendimento.strftime("%Y-%m-%d") if a.data_atendimento else None, "tipo_servico": a.tipo_servico}
            for a in atendimentos
        ]
        resumo = ai_module.gerar_resumo_cliente(atendimentos_dict)
        return {"resumo": resumo}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})

# 3. IA Sugestora de Ações
@app.get("/ia/sugestoes/{empresa_id}")
def ia_sugestoes(empresa_id: int):
    try:
        from database import SessionLocal
        db = SessionLocal()
        clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa_id).all()
        clientes_list = []
        for c in clientes:
            atendimentos = db.query(models.Atendimento).filter(models.Atendimento.cliente_id == c.id).all()
            atendimentos_dict = [
                {"data": a.data_atendimento.strftime("%Y-%m-%d") if a.data_atendimento else None, "tipo_servico": a.tipo_servico}
                for a in atendimentos
            ]
            clientes_list.append({
                "nome": c.nome,
                "atendimentos": atendimentos_dict,
                "status_ia_cliente": ai_module.analisar_cliente(atendimentos_dict)
            })
        sugestoes = ai_module.sugerir_acoes(clientes_list)
        return {"sugestoes": sugestoes}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})

# 4. IA Insights do Negócio
@app.get("/ia/insights/{empresa_id}")
def ia_insights(empresa_id: int):
    try:
        from database import SessionLocal
        db = SessionLocal()
        clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa_id).all()
        atendimentos = db.query(models.Atendimento).filter(models.Atendimento.empresa_id == empresa_id).all()
        clientes_dict = [
            {"id": c.id, "nome": c.nome} for c in clientes
        ]
        atendimentos_dict = [
            {"id": a.id, "cliente_id": a.cliente_id, "data": a.data_atendimento.strftime("%Y-%m-%d") if a.data_atendimento else None}
            for a in atendimentos
        ]
        insights = ai_module.gerar_insights_empresa(clientes_dict, atendimentos_dict)
        return {"insights": insights}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})

# 5. Assistente IA Interno
class PerguntaIA(BaseModel):
    pergunta: str
    empresa_id: int

@app.post("/ia/perguntar")
def ia_perguntar(body: PerguntaIA):
    try:
        from database import SessionLocal
        db = SessionLocal()
        # Gerar contexto textual dos clientes e atendimentos da empresa
        clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == body.empresa_id).all()
        atendimentos = db.query(models.Atendimento).filter(models.Atendimento.empresa_id == body.empresa_id).all()
        contexto = f"Clientes: {[c.nome for c in clientes]}\nAtendimentos: {len(atendimentos)}"
        resposta = ai_module.responder_pergunta(body.pergunta, contexto)
        return {"resposta": resposta}
    except Exception as e:
        return JSONResponse(status_code=500, content={"erro": str(e)})
# ====================================================



# ========== ROTA DE DASHBOARD ========== 


@app.get("/api/dashboard")
def obter_dashboard(
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Retorna estatísticas do dashboard
    """
    empresa = get_current_empresa(token, db)

    total_clientes = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id
    ).count()

    total_atendimentos = db.query(models.Atendimento).filter(
        models.Atendimento.empresa_id == empresa.id
    ).count()

    # Últimos 5 atendimentos
    ultimos_atendimentos = db.query(
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

    # Top 5 clientes mais ativos (com mais atendimentos)
    from sqlalchemy import func
    top_clientes_query = (
        db.query(
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
    from sqlalchemy import asc
    intervalos = []
    clientes_ids = db.query(models.Cliente.id).filter(models.Cliente.empresa_id == empresa.id).all()
    for (cid,) in clientes_ids:
        atendimentos = db.query(models.Atendimento).filter(
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
    clientes_novos_mes = db.query(models.Cliente).filter(
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


# ========== ROTA RAIZ ==========

@app.get("/")
def root():
    """
    Rota raiz da API
    """
    return {
        "message": "ClientFlow API v1.0.0",
        "status": "online",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
