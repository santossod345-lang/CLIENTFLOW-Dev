"""
SaaS Models - Fase 5: Preparação para monetização
Modelos para planos, subscriptions, uso e billing
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, BigInteger
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from backend.database import Base


class PlanType(Base):
    """Tipos de plano disponíveis (Free, Pro, Enterprise)"""
    __tablename__ = "plan_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # free, pro, enterprise
    display_name = Column(String(100), nullable=False)      # "Gratuito", "Profissional", etc
    price_monthly = Column(Float, default=0.0)               # Preço em USD
    max_companies = Column(Integer, default=1)               # Empresas permitidas
    max_clients_per_company = Column(Integer, default=100)   # Clientes por empresa
    max_services_per_company = Column(Integer, default=500)  # Serviços por empresa
    features = Column(String(2000), default="")              # Features em JSON
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    subscriptions = relationship("Subscription", back_populates="plan")


class Subscription(Base):
    """Subscription de uma empresa a um plano"""
    __tablename__ = "subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    empresa_id = Column(Integer, ForeignKey("empresas.id"), unique=True, nullable=False)
    plan_id = Column(Integer, ForeignKey("plan_types.id"), nullable=False)
    status = Column(String(20), default="active")            # active, cancelled, suspended
    started_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ends_at = Column(DateTime, nullable=True)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    empresa = relationship("Empresa", backref="subscription")
    plan = relationship("PlanType", back_populates="subscriptions")
    invoices = relationship("Invoice", back_populates="subscription")
    usage_records = relationship("UsageRecord", back_populates="subscription")


class UsageRecord(Base):
    """Registro de uso para billing"""
    __tablename__ = "usage_records"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    metric_type = Column(String(50), nullable=False)         # "clients", "services", "api_calls"
    value = Column(BigInteger, default=0)                    # Valor do uso
    period_date = Column(DateTime, nullable=False)           # Data do período
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    subscription = relationship("Subscription", back_populates="usage_records")


class Invoice(Base):
    """Fatura gerada"""
    __tablename__ = "invoices"
    
    id = Column(Integer, primary_key=True, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=False)
    status = Column(String(20), default="pending")           # pending, paid, failed, refunded
    amount = Column(Float, nullable=False)
    currency = Column(String(3), default="USD")
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    issued_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    due_date = Column(DateTime, nullable=False)
    paid_at = Column(DateTime, nullable=True)
    
    subscription = relationship("Subscription", back_populates="invoices")


class Feature(Base):
    """Features do sistema para controle de acesso"""
    __tablename__ = "features"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)  # "api_access", "ai_assistant", etc
    display_name = Column(String(200), nullable=False)
    description = Column(String(500))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class FeatureAccess(Base):
    """Controle de acesso a features por plano"""
    __tablename__ = "feature_access"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plan_types.id"), nullable=False)
    feature_id = Column(Integer, ForeignKey("features.id"), nullable=False)
    enabled = Column(Boolean, default=False)
    limit = Column(Integer, nullable=True)  # limite de uso, NULL = ilimitado
