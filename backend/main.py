"""
API Principal do ClientFlow - Sistema SaaS Multi-Tenant
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

import database
import models
import auth

# Criar tabelas no banco de dados
models.Base.metadata.create_all(bind=database.engine)

# Inicializar FastAPI
app = FastAPI(title="ClientFlow API", version="1.0.0")

# Configurar CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ========== SCHEMAS PYDANTIC ==========

class EmpresaCreate(BaseModel):
    nome_empresa: str
    nicho: str
    telefone: str
    email_login: EmailStr
    senha: str


class EmpresaLogin(BaseModel):
    email_login: EmailStr
    senha: str


class EmpresaResponse(BaseModel):
    id: int
    nome_empresa: str
    nicho: str
    telefone: str
    email_login: str
    data_cadastro: datetime
    
    class Config:
        from_attributes = True


class ClienteCreate(BaseModel):
    nome: str
    telefone: str


class ClienteResponse(BaseModel):
    id: int
    empresa_id: int
    nome: str
    telefone: str
    data_primeiro_contato: datetime
    
    class Config:
        from_attributes = True


class AtendimentoCreate(BaseModel):
    cliente_id: int
    tipo: str
    descricao: str
    veiculo: Optional[str] = None


class AtendimentoResponse(BaseModel):
    id: int
    empresa_id: int
    cliente_id: int
    tipo: str
    descricao: str
    veiculo: Optional[str]
    data: datetime
    
    class Config:
        from_attributes = True


class AtendimentoDetailResponse(AtendimentoResponse):
    cliente_nome: str
    cliente_telefone: str
    
    class Config:
        from_attributes = True


# ========== SISTEMA DE SESSÃO SIMPLES ==========
# Em produção, usar JWT ou Redis
active_sessions = {}  # {token: empresa_id}


def get_current_empresa(token: str, db: Session = Depends(database.get_db)) -> models.Empresa:
    """
    Valida o token de sessão e retorna a empresa autenticada
    """
    if token not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada"
        )
    
    empresa_id = active_sessions[token]
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empresa não encontrada"
        )
    
    return empresa


# ========== ROTAS DE AUTENTICAÇÃO ==========

@app.post("/api/empresas/cadastrar", response_model=EmpresaResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(empresa: EmpresaCreate, db: Session = Depends(database.get_db)):
    """
    Cadastra uma nova empresa no sistema
    """
    # Verificar se o email já existe
    existing = db.query(models.Empresa).filter(models.Empresa.email_login == empresa.email_login).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar hash da senha
    senha_hash = auth.get_password_hash(empresa.senha)
    
    # Criar nova empresa
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
def login_empresa(login: EmpresaLogin, db: Session = Depends(database.get_db)):
    """
    Realiza login e retorna token de sessão
    """
    # Buscar empresa pelo email
    empresa = db.query(models.Empresa).filter(models.Empresa.email_login == login.email_login).first()
    
    if not empresa:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Verificar senha
    if not auth.verify_password(login.senha, empresa.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos"
        )
    
    # Criar token de sessão
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
    """
    Realiza logout removendo o token de sessão
    """
    if token in active_sessions:
        del active_sessions[token]
    
    return {"message": "Logout realizado com sucesso"}


# ========== ROTAS DE CLIENTES ==========

@app.post("/api/clientes", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente: ClienteCreate, 
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Cria um novo cliente vinculado à empresa autenticada
    """
    empresa = get_current_empresa(token, db)
    
    novo_cliente = models.Cliente(
        empresa_id=empresa.id,
        nome=cliente.nome,
        telefone=cliente.telefone
    )
    
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    
    return novo_cliente


@app.get("/api/clientes", response_model=List[ClienteResponse])
def listar_clientes(
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Lista todos os clientes da empresa autenticada
    """
    empresa = get_current_empresa(token, db)
    
    clientes = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id
    ).order_by(models.Cliente.data_primeiro_contato.desc()).all()
    
    return clientes


@app.get("/api/clientes/{cliente_id}", response_model=ClienteResponse)
def obter_cliente(
    cliente_id: int,
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Obtém detalhes de um cliente específico
    """
    empresa = get_current_empresa(token, db)
    
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == cliente_id,
        models.Cliente.empresa_id == empresa.id
    ).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    return cliente


# ========== ROTAS DE ATENDIMENTOS ==========

@app.post("/api/atendimentos", response_model=AtendimentoResponse, status_code=status.HTTP_201_CREATED)
def criar_atendimento(
    atendimento: AtendimentoCreate,
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Registra um novo atendimento
    """
    empresa = get_current_empresa(token, db)
    
    # Verificar se o cliente pertence à empresa
    cliente = db.query(models.Cliente).filter(
        models.Cliente.id == atendimento.cliente_id,
        models.Cliente.empresa_id == empresa.id
    ).first()
    
    if not cliente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cliente não encontrado"
        )
    
    novo_atendimento = models.Atendimento(
        empresa_id=empresa.id,
        cliente_id=atendimento.cliente_id,
        tipo=atendimento.tipo,
        descricao=atendimento.descricao,
        veiculo=atendimento.veiculo
    )
    
    db.add(novo_atendimento)
    db.commit()
    db.refresh(novo_atendimento)
    
    return novo_atendimento


@app.get("/api/atendimentos", response_model=List[AtendimentoDetailResponse])
def listar_atendimentos(
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Lista todos os atendimentos da empresa com detalhes do cliente
    """
    empresa = get_current_empresa(token, db)
    
    atendimentos = db.query(
        models.Atendimento,
        models.Cliente.nome.label("cliente_nome"),
        models.Cliente.telefone.label("cliente_telefone")
    ).join(
        models.Cliente, models.Atendimento.cliente_id == models.Cliente.id
    ).filter(
        models.Atendimento.empresa_id == empresa.id
    ).order_by(models.Atendimento.data.desc()).all()
    
    # Formatar resposta
    resultado = []
    for atendimento, cliente_nome, cliente_telefone in atendimentos:
        resultado.append({
            "id": atendimento.id,
            "empresa_id": atendimento.empresa_id,
            "cliente_id": atendimento.cliente_id,
            "tipo": atendimento.tipo,
            "descricao": atendimento.descricao,
            "veiculo": atendimento.veiculo,
            "data": atendimento.data,
            "cliente_nome": cliente_nome,
            "cliente_telefone": cliente_telefone
        })
    
    return resultado


@app.get("/api/atendimentos/{atendimento_id}", response_model=AtendimentoDetailResponse)
def obter_atendimento(
    atendimento_id: int,
    token: str,
    db: Session = Depends(database.get_db)
):
    """
    Obtém detalhes de um atendimento específico
    """
    empresa = get_current_empresa(token, db)
    
    resultado = db.query(
        models.Atendimento,
        models.Cliente.nome.label("cliente_nome"),
        models.Cliente.telefone.label("cliente_telefone")
    ).join(
        models.Cliente, models.Atendimento.cliente_id == models.Cliente.id
    ).filter(
        models.Atendimento.id == atendimento_id,
        models.Atendimento.empresa_id == empresa.id
    ).first()
    
    if not resultado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Atendimento não encontrado"
        )
    
    atendimento, cliente_nome, cliente_telefone = resultado
    
    return {
        "id": atendimento.id,
        "empresa_id": atendimento.empresa_id,
        "cliente_id": atendimento.cliente_id,
        "tipo": atendimento.tipo,
        "descricao": atendimento.descricao,
        "veiculo": atendimento.veiculo,
        "data": atendimento.data,
        "cliente_nome": cliente_nome,
        "cliente_telefone": cliente_telefone
    }


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
    ).order_by(models.Atendimento.data.desc()).limit(5).all()
    
    atendimentos_recentes = []
    for atendimento, cliente_nome in ultimos_atendimentos:
        atendimentos_recentes.append({
            "id": atendimento.id,
            "cliente_nome": cliente_nome,
            "tipo": atendimento.tipo,
            "data": atendimento.data.strftime("%d/%m/%Y %H:%M")
        })
    
    return {
        "empresa": {
            "nome": empresa.nome_empresa,
            "nicho": empresa.nicho
        },
        "estatisticas": {
            "total_clientes": total_clientes,
            "total_atendimentos": total_atendimentos
        },
        "atendimentos_recentes": atendimentos_recentes
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
