
"""
Modelos do banco de dados representando empresas, clientes e atendimentos
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, declared_attr
from datetime import datetime, timezone
from backend.database import Base

# Constantes de configuração de relacionamentos
CASCADE_DELETE_ORPHAN = "all, delete-orphan"
EMPRESA_FK = "empresas.id"
CLIENTE_FK = "clientes.id"

# Suporte a schema dinâmico para multi-tenant
class BaseModel(Base):
    __abstract__ = True
    @declared_attr
    def __table_args__(cls):
        schema = getattr(cls, "__schema__", None)
        if schema:
            return {"schema": schema}
        return {}


class LogAcao(BaseModel):
    __tablename__ = "logs_acoes"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String)
    acao = Column(String)
    entidade = Column(String)
    entidade_id = Column(Integer)
    data = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    detalhes = Column(Text)


class Empresa(BaseModel):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True, index=True)
    nome_empresa = Column(String, nullable=False)
    nicho = Column(String, nullable=False)
    tipo_empresa = Column(String, default="generico")
    telefone = Column(String)
    email_login = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    data_cadastro = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    plano_empresa = Column(String, default="free")
    data_inicio_plano = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ativo = Column(Integer, default=1)
    limite_clientes = Column(Integer, default=1000)
    limite_atendimentos = Column(Integer, default=5000)
    clientes = relationship("Cliente", back_populates="empresa", cascade=CASCADE_DELETE_ORPHAN)
    atendimentos = relationship("Atendimento", back_populates="empresa", cascade=CASCADE_DELETE_ORPHAN)


class RefreshToken(BaseModel):
    __tablename__ = "refresh_tokens"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey(EMPRESA_FK), nullable=False, index=True)
    jti = Column(String(64), unique=True, index=True, nullable=False)
    token_hash = Column(String(128), index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=True, index=True)
    revoked = Column(Integer, default=0)
    replaced_by = Column(String(64), nullable=True, index=True)
    user_agent = Column(String, nullable=True)
    ip_address = Column(String, nullable=True)
    empresa = relationship("Empresa", backref="refresh_tokens")


class Cliente(BaseModel):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey(EMPRESA_FK), nullable=False)
    nome = Column(String, nullable=False)
    telefone = Column(String)
    origem_cliente = Column(String, default="Outro")
    cidade = Column(String)
    bairro = Column(String)
    aniversario = Column(String)
    observacoes = Column(Text)
    data_primeiro_contato = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status_cliente = Column(String, default="novo")
    status_ia_cliente = Column(String, nullable=True)
    nivel_atividade = Column(String, default="baixo")
    score_atividade = Column(Integer, default=0)
    vip = Column(Integer, default=0)
    inativo = Column(Integer, default=0)
    importante = Column(Integer, default=0)
    anotacoes_rapidas = Column(Text, default="")
    empresa = relationship("Empresa", back_populates="clientes")
    atendimentos = relationship("Atendimento", back_populates="cliente", cascade=CASCADE_DELETE_ORPHAN)


class Atendimento(BaseModel):
    __tablename__ = "atendimentos"
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey(EMPRESA_FK), nullable=False)
    cliente_id = Column(Integer, ForeignKey(CLIENTE_FK), nullable=False)
    tipo_servico = Column(String, nullable=False)
    status_atendimento = Column(String, default="Novo")
    descricao_servico = Column(Text)
    valor_cobrado = Column(String)
    forma_pagamento = Column(String)
    funcionario_responsavel = Column(String)
    duracao_servico = Column(String)
    descricao_detalhada = Column(Text)
    concluido = Column(Integer, default=0)
    pendente = Column(Integer, default=0)
    meses_retorno = Column(Integer)
    data_proxima_revisao = Column(DateTime)
    data_atendimento = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    empresa = relationship("Empresa", back_populates="atendimentos")
    cliente = relationship("Cliente", back_populates="atendimentos")
