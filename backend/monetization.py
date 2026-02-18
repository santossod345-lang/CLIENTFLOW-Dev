"""
Monetization Module - SaaS Billing, Planos, Feature Gating
FASE 5: SaaS Monetization
"""

from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime, timedelta

from backend.utils import get_logger

logger = get_logger("clientflow.monetization")


class PlanTier(str, Enum):
    """Tipos de planos"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Plan:
    """Definição de um plano"""
    
    def __init__(
        self,
        tier: PlanTier,
        name: str,
        price_monthly: float,
        features: Dict[str, any],
        limits: Dict[str, int],
    ):
        self.tier = tier
        self.name = name
        self.price_monthly = price_monthly
        self.features = features
        self.limits = limits
    
    def can_access_feature(self, feature: str) -> bool:
        """Verifica se plano tem acesso a feature"""
        return self.features.get(feature, False)
    
    def get_limit(self, limit_name: str) -> Optional[int]:
        """Obtém limite para feature"""
        return self.limits.get(limit_name)


# Definição dos planos SaaS
PLANS = {
    PlanTier.FREE: Plan(
        tier=PlanTier.FREE,
        name="Plano Gratuito",
        price_monthly=0,
        features={
            "clientes": True,
            "atendimentos": True,
            "dashboard": True,
            "csv_export": False,
            "whatsapp_integration": False,
            "analytics_advanced": False,
            "api_access": False,
            "support_email": False,
        },
        limits={
            "max_clientes": 100,
            "max_atendimentos": 1000,
            "max_usuarios": 1,
            "api_requests_per_day": 0,  # Sem acesso
        }
    ),
    
    PlanTier.PRO: Plan(
        tier=PlanTier.PRO,
        name="Plano Profissional",
        price_monthly=99.00,
        features={
            "clientes": True,
            "atendimentos": True,
            "dashboard": True,
            "csv_export": True,
            "whatsapp_integration": True,
            "analytics_advanced": True,
            "api_access": True,
            "support_email": True,
        },
        limits={
            "max_clientes": 10000,
            "max_atendimentos": 100000,
            "max_usuarios": 5,
            "api_requests_per_day": 100000,
        }
    ),
    
    PlanTier.ENTERPRISE: Plan(
        tier=PlanTier.ENTERPRISE,
        name="Plano Enterprise",
        price_monthly=999.00,
        features={
            "clientes": True,
            "atendimentos": True,
            "dashboard": True,
            "csv_export": True,
            "whatsapp_integration": True,
            "analytics_advanced": True,
            "api_access": True,
            "support_email": True,
            # Enterprise features
            "custom_domain": True,
            "sso": True,
            "custom_api": True,
            "phone_support": True,
            "dedicated_account_manager": True,
        },
        limits={
            "max_clientes": 999999,
            "max_atendimentos": 999999,
            "max_usuarios": 999,
            "api_requests_per_day": 999999,
        }
    ),
}


class Subscription:
    """Representação de uma subscription"""
    
    def __init__(
        self,
        empresa_id: int,
        plan_tier: PlanTier,
        start_date: datetime,
        renewal_date: datetime,
        is_active: bool = True,
        payment_status: str = "active",
    ):
        self.empresa_id = empresa_id
        self.plan_tier = plan_tier
        self.plan = PLANS[plan_tier]
        self.start_date = start_date
        self.renewal_date = renewal_date
        self.is_active = is_active
        self.payment_status = payment_status
    
    def is_expired(self) -> bool:
        """Verifica se subscription expirou"""
        return datetime.now() > self.renewal_date
    
    def days_until_renewal(self) -> int:
        """Dias até renovação"""
        delta = self.renewal_date - datetime.now()
        return max(0, delta.days)
    
    def get_plan(self) -> Plan:
        """Obtém plano atual"""
        return self.plan


class FeatureGate:
    """
    Feature gating baseado em plano
    Controla acesso a features por plano
    """
    
    @staticmethod
    def can_access(plan_tier: PlanTier, feature: str) -> bool:
        """Verifica se plano pode acessar feature"""
        plan = PLANS.get(plan_tier)
        if not plan:
            return False
        
        return plan.can_access_feature(feature)
    
    @staticmethod
    def get_feature_access(plan_tier: PlanTier) -> Dict[str, bool]:
        """Obtém todas as features acessíveis do plano"""
        plan = PLANS.get(plan_tier)
        if not plan:
            return {}
        
        return plan.features
    
    @staticmethod
    def check_limit(
        plan_tier: PlanTier,
        limit_name: str,
        current_value: int
    ) -> bool:
        """
        Verifica se valor está dentro do limite
        
        Returns: True se está dentro do limite, False se excedeu
        """
        plan = PLANS.get(plan_tier)
        if not plan:
            return False
        
        limit = plan.get_limit(limit_name)
        if limit is None:
            return True  # Sem limite definido
        
        return current_value < limit


class BillingCycle:
    """Gerencia ciclos de billing"""
    
    @staticmethod
    def get_next_billing_date(start_date: datetime) -> datetime:
        """Calcula próxima data de billing (mensal)"""
        # Adiciona 1 mês
        if start_date.month == 12:
            return start_date.replace(year=start_date.year + 1, month=1)
        else:
            return start_date.replace(month=start_date.month + 1)
    
    @staticmethod
    def calculate_pro_rata(
        plan_tier: PlanTier,
        days_used: int,
        total_days: int = 30
    ) -> float:
        """
        Calcula cobrança pro-rata
        Útil para upgrades/downgrades mid-cycle
        """
        plan = PLANS.get(plan_tier)
        if not plan:
            return 0.0
        
        daily_price = plan.price_monthly / total_days
        return round(daily_price * days_used, 2)


class Usage:
    """Rastreia uso do cliente"""
    
    def __init__(self, empresa_id: int):
        self.empresa_id = empresa_id
        self.metrics = {
            "clientes": 0,
            "atendimentos": 0,
            "usuarios": 1,
            "api_calls": 0,
            "exports": 0,
        }
    
    def increment(self, metric: str, amount: int = 1):
        """Incrementa métrica de uso"""
        if metric in self.metrics:
            self.metrics[metric] += amount
            logger.debug(f"Usage incremented: {metric} += {amount}")
    
    def get_usage_percentage(self, plan_tier: PlanTier, metric: str) -> float:
        """
        Calcula percentual de uso vs limite
        
        Returns: 0.0 a 1.0 (0% a 100%)
        """
        plan = PLANS.get(plan_tier)
        if not plan:
            return 0.0
        
        limit_name = f"max_{metric}"
        limit = plan.get_limit(limit_name)
        
        if limit is None or limit == 0:
            return 0.0
        
        current = self.metrics.get(metric, 0)
        return min(1.0, current / limit)


class InvoiceGenerator:
    """Gera faturas para subscriptions"""
    
    @staticmethod
    def generate_invoice(
        empresa_id: int,
        subscription: Subscription,
        period_start: datetime,
        period_end: datetime,
    ) -> Dict:
        """Gera fatura para período"""
        plan = subscription.plan
        
        days_in_period = (period_end - period_start).days
        invoice = {
            "empresa_id": empresa_id,
            "plan_tier": subscription.plan_tier.value,
            "plan_name": plan.name,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "days": days_in_period,
            "subtotal": plan.price_monthly,
            "tax": round(plan.price_monthly * 0.15, 2),  # 15% tax
            "total": round(plan.price_monthly * 1.15, 2),
            "status": "pending",
            "due_date": (period_end + timedelta(days=15)).isoformat(),
        }
        
        logger.info(f"Invoice generated for empresa {empresa_id}: {invoice['total']}")
        return invoice


# Exemplo de como adicionar ao modelo Empresa:
"""
class Empresa(Base):
    __tablename__ = "empresas"
    
    # ... campos existentes ...
    
    # Campos de monetização
    plano = Column(String, default=PlanTier.FREE.value)
    subscription_active = Column(Integer, default=1)
    billing_cycle_start = Column(DateTime, default=datetime.utcnow)
    billing_cycle_end = Column(DateTime, default=datetime.utcnow)
    
    # Métodos
    def get_subscription(self) -> Subscription:
        return Subscription(
            empresa_id=self.id,
            plan_tier=PlanTier(self.plano),
            start_date=self.billing_cycle_start,
            renewal_date=self.billing_cycle_end,
            is_active=bool(self.subscription_active),
        )
    
    def can_access_feature(self, feature: str) -> bool:
        return FeatureGate.can_access(PlanTier(self.plano), feature)
    
    def get_remaining_clients_quota(self) -> int:
        clients = db.query(Cliente).filter(Cliente.empresa_id == self.id).count()
        limit = PLANS[PlanTier(self.plano)].get_limit("max_clientes")
        return max(0, (limit or 999999) - clients)
"""
