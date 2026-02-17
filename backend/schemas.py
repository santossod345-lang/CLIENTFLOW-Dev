
from pydantic import BaseModel
from datetime import datetime

class EmpresaOut(BaseModel):
    id: int
    nome_empresa: str
    nicho: str
    telefone: str | None = None
    email_login: str
    tipo_empresa: str | None = None
    plano_empresa: str | None = None
    limite_clientes: int | None = None
    limite_atendimentos: int | None = None
    ativo: int | None = None
    model_config = {
        "from_attributes": True
    }

class EmpresaLogin(BaseModel):
    email_login: str
    senha: str
    model_config = {
        "from_attributes": True
    }


class RefreshRequest(BaseModel):
    refresh_token: str
    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    model_config = {
        "from_attributes": True
    }


class EmpresaCreate(BaseModel):
    nome_empresa: str
    nicho: str
    telefone: str | None = None
    email_login: str
    senha: str
    tipo_empresa: str | None = None
    plano_empresa: str | None = None
    limite_clientes: int | None = None
    limite_atendimentos: int | None = None
    model_config = {
        "from_attributes": True
    }

class ClienteCreate(BaseModel):
    nome: str
    telefone: str
    anotacoes_rapidas: str = ""
    model_config = {
        "from_attributes": True
    }

class AtendimentoCreate(BaseModel):
    tipo: str
    descricao: str
    veiculo: str
    model_config = {
        "from_attributes": True
    }

class ClienteOut(BaseModel):
    id: int
    nome: str
    telefone: str
    anotacoes_rapidas: str = ""
    data_primeiro_contato: datetime
    model_config = {
        "from_attributes": True
    }

class PerguntaIA(BaseModel):
    pergunta: str
    model_config = {
        "from_attributes": True
    }
