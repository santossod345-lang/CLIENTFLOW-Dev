
"""
Modelos do banco de dados representando empresas, clientes e atendimentos
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# ...existing code...

class LogAcao(Base):
    __tablename__ = "logs_acoes"
    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String)
    acao = Column(String)
    entidade = Column(String)
    entidade_id = Column(Integer)
    data = Column(DateTime, default=datetime.utcnow)
    detalhes = Column(Text)


class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_empresa = Column(String, nullable=False)
    nicho = Column(String, nullable=False)
    tipo_empresa = Column(String, default="generico")  # Para multi-nicho
    telefone = Column(String)
    email_login = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    plano_empresa = Column(String, default="free")
    data_inicio_plano = Column(DateTime, default=datetime.utcnow)
    ativo = Column(Integer, default=1)  # 1=ativo, 0=inativo
    limite_clientes = Column(Integer, default=1000)
    limite_atendimentos = Column(Integer, default=5000)
    
    # Relacionamentos
    clientes = relationship("Cliente", back_populates="empresa", cascade="all, delete-orphan")
    atendimentos = relationship("Atendimento", back_populates="empresa", cascade="all, delete-orphan")


class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nome = Column(String, nullable=False)
    telefone = Column(String)
    origem_cliente = Column(String, default="Outro")  # WhatsApp, Instagram, Indicação, Google, Outro
    cidade = Column(String)  # Novo campo
    bairro = Column(String)  # Novo campo
    aniversario = Column(String)  # Novo campo (formato: 'dd/mm')
    observacoes = Column(Text)  # Novo campo
    data_primeiro_contato = Column(DateTime, default=datetime.utcnow)
    status_cliente = Column(String, default="novo")  # novo, frequente, inativo
    status_ia_cliente = Column(String, nullable=True)  # Campo IA (opcional)
    nivel_atividade = Column(String, default="baixo")  # baixo, medio, alto
    score_atividade = Column(Integer, default=0)
    vip = Column(Integer, default=0)  # 1=VIP, 0=normal
    inativo = Column(Integer, default=0)  # 1=inativo, 0=ativo
    importante = Column(Integer, default=0)  # 1=importante, 0=normal
    anotacoes_rapidas = Column(Text, default="")  # Campo para anotações rápidas
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="clientes")
    atendimentos = relationship("Atendimento", back_populates="cliente", cascade="all, delete-orphan")


class Atendimento(Base):
    __tablename__ = "atendimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo_servico = Column(String, nullable=False)  # Ex: "manutenção", "revisão", "retorno", "outros"
    status_atendimento = Column(String, default="Novo")  # Novo, Em andamento, Concluído
    descricao_servico = Column(Text)
    valor_cobrado = Column(String)  # Novo campo
    forma_pagamento = Column(String)  # Novo campo
    funcionario_responsavel = Column(String)  # Novo campo
    duracao_servico = Column(String)  # Novo campo
    descricao_detalhada = Column(Text)  # Novo campo
    concluido = Column(Integer, default=0)  # 1=concluído, 0=não
    pendente = Column(Integer, default=0)  # 1=pendente, 0=não
    meses_retorno = Column(Integer)  # Quantidade de meses para retorno sugerido
    data_proxima_revisao = Column(DateTime)  # Data prevista para retorno
    data_atendimento = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="atendimentos")
    cliente = relationship("Cliente", back_populates="atendimentos")
