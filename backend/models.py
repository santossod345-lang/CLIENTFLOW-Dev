"""
Modelos do banco de dados representando empresas, clientes e atendimentos
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Empresa(Base):
    __tablename__ = "empresas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome_empresa = Column(String, nullable=False)
    nicho = Column(String, nullable=False)
    telefone = Column(String)
    email_login = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    clientes = relationship("Cliente", back_populates="empresa", cascade="all, delete-orphan")
    atendimentos = relationship("Atendimento", back_populates="empresa", cascade="all, delete-orphan")


class Cliente(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    nome = Column(String, nullable=False)
    telefone = Column(String)
    data_primeiro_contato = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="clientes")
    atendimentos = relationship("Atendimento", back_populates="cliente", cascade="all, delete-orphan")


class Atendimento(Base):
    __tablename__ = "atendimentos"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    tipo = Column(String, nullable=False)  # Ex: "Orçamento", "Reparo", "Revisão"
    descricao = Column(Text)
    veiculo = Column(String)  # Ex: "Honda Civic 2020"
    data = Column(DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    empresa = relationship("Empresa", back_populates="atendimentos")
    cliente = relationship("Cliente", back_populates="atendimentos")
