"""
Subscriptions Router - Gerenciamento de planos e billing
Implementa endpoints para gerenciar subscriptions SaaS
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional

from backend.responses import success_response, error_response
from backend.exceptions import NotFoundError, AuthorizationError, ConflictError
from backend.utils import log_action, log_error, get_logger
from backend.monetization import (
    PLANS, PlanTier, FeatureGate, BillingCycle,
    Usage, InvoiceGenerator, Subscription
)

logger = get_logger("clientflow.routers.subscriptions")

router = APIRouter(
    prefix="/api/subscriptions",
    tags=["subscriptions"],
    responses={404: {"description": "Not found"}},
)


@router.get("/plans")
async def list_plans():
    """
    Lista todos os planos disponíveis
    Pública - sem autenticação necessária
    """
    plans_data = []
    
    for tier, plan in PLANS.items():
        plans_data.append({
            "tier": tier.value,
            "name": plan.name,
            "price_monthly": plan.price_monthly,
            "features": plan.features,
            "limits": plan.limits,
        })
    
    logger.info(f"Listed {len(plans_data)} plans")
    return success_response(
        data={"plans": plans_data},
        message="Planos disponíveis"
    )


@router.get("/plans/{tier}/details")
async def get_plan_details(tier: str):
    """Obtém detalhes de um plano específico"""
    try:
        plan_tier = PlanTier(tier)
    except ValueError:
        raise NotFoundError(f"Plano '{tier}' não encontrado")
    
    plan = PLANS.get(plan_tier)
    if not plan:
        raise NotFoundError(f"Plano '{tier}' indisponível")
    
    return success_response(
        data={
            "tier": plan_tier.value,
            "name": plan.name,
            "price_monthly": plan.price_monthly,
            "features": plan.features,
            "limits": plan.limits,
            "description": f"Plano com até {plan.get_limit('max_clientes')} clientes"
        },
        message=f"Detalhes do plano {plan.name}"
    )


@router.post("/upgrade/{empresa_id}")
async def upgrade_subscription(empresa_id: int, new_tier: str):
    """
    Fazer upgrade de subscription
    
    Em produção, integrar com Stripe/Gateway de pagamento
    """
    try:
        new_plan_tier = PlanTier(new_tier)
    except ValueError:
        raise NotFoundError(f"Plano '{new_tier}' inválido")
    
    # TODO: Buscar empresa do banco de dados
    # TODO: Validar autenticação (only empresa owner)
    # TODO: Processar pagamento via Stripe
    # TODO: Calcular pro-rata se mid-cycle
    # TODO: Atualizar subscription no banco
    
    log_action(
        action="upgrade",
        entity="subscription",
        entity_id=empresa_id,
        usuario_id=empresa_id,
        details={"new_tier": new_tier}
    )
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "new_plan": new_tier,
            "effective_date": datetime.now().isoformat(),
        },
        message=f"Upgrade para plano {new_tier} realizado com sucesso"
    )


@router.post("/downgrade/{empresa_id}")
async def downgrade_subscription(empresa_id: int, new_tier: str):
    """Fazer downgrade de subscription"""
    try:
        new_plan_tier = PlanTier(new_tier)
    except ValueError:
        raise NotFoundError(f"Plano '{new_tier}' inválido")
    
    # Downgrade geralmente efetiva no próximo ciclo
    next_cycle = datetime.now() + timedelta(days=30)
    
    log_action(
        action="downgrade",
        entity="subscription",
        entity_id=empresa_id,
        usuario_id=empresa_id,
        details={"new_tier": new_tier, "effective_date": next_cycle.isoformat()}
    )
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "current_plan": "pro",  # TODO: buscar do banco
            "new_plan": new_tier,
            "effective_date": next_cycle.isoformat(),
            "note": "Downgrade efetivará no próximo ciclo de billing"
        },
        message="Downgrade agendado com sucesso"
    )


@router.get("/status/{empresa_id}")
async def get_subscription_status(empresa_id: int):
    """Obtém status da subscription da empresa"""
    # TODO: Buscar do banco de dados
    # Dados mocados para exemplo
    
    subscription = Subscription(
        empresa_id=empresa_id,
        plan_tier=PlanTier.PRO,
        start_date=datetime.now(),
        renewal_date=datetime.now() + timedelta(days=30),
        is_active=True,
    )
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "plan": subscription.plan_tier.value,
            "plan_name": subscription.plan.name,
            "is_active": subscription.is_active,
            "start_date": subscription.start_date.isoformat(),
            "renewal_date": subscription.renewal_date.isoformat(),
            "days_until_renewal": subscription.days_until_renewal(),
            "payment_status": subscription.payment_status,
        },
        message="Status da subscription"
    )


@router.get("/invoices/{empresa_id}")
async def list_invoices(empresa_id: int, skip: int = 0, limit: int = 20):
    """Lista faturas da empresa"""
    # TODO: Buscar faturas do banco de dados
    
    invoices = []
    
    log_action(
        action="list_invoices",
        entity="empresa",
        entity_id=empresa_id,
        usuario_id=empresa_id,
    )
    
    return success_response(
        data={
            "invoices": invoices,
            "total": 0,
        },
        message="Faturas da empresa"
    )


@router.post("/cancel/{empresa_id}")
async def cancel_subscription(empresa_id: int):
    """Cancela subscription (com aviso prévio)"""
    # TODO: Validar autenticação
    # TODO: Aplicar período de carência (ex: 30 dias)
    # TODO: Atualizar status no banco
    
    log_action(
        action="cancel",
        entity="subscription",
        entity_id=empresa_id,
        usuario_id=empresa_id,
        details={"reason": "requested_by_user"}
    )
    
    cancellation_date = datetime.now() + timedelta(days=30)
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "status": "to_be_cancelled",
            "cancellation_date": cancellation_date.isoformat(),
            "note": "Subscription será cancelada em 30 dias. Você pode reverter este pedido."
        },
        message="Cancelamento agendado com sucesso"
    )


@router.get("/feature-access/{empresa_id}")
async def get_feature_access(empresa_id: int):
    """
    Obtém quais features a empresa tem acesso
    Útil para frontend fazer feature gating
    """
    # TODO: Buscar plano do banco de dados
    plan_tier = PlanTier.PRO  # Exemplo
    
    features = FeatureGate.get_feature_access(plan_tier)
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "plan": plan_tier.value,
            "features": features,
        },
        message="Features acessíveis desta empresa"
    )


@router.get("/usage/{empresa_id}")
async def get_usage_stats(empresa_id: int):
    """
    Obtém estatísticas de uso vs limites
    Mostra quanto da cota já foi utilizado
    """
    # TODO: Buscar dados do banco
    # Exemplo mocado
    
    plan_tier = PlanTier.PRO
    usage = Usage(empresa_id)
    usage.increment("clientes", 45)
    usage.increment("atendimentos", 250)
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "plan": plan_tier.value,
            "usage": {
                "clientes": {
                    "current": usage.metrics["clientes"],
                    "limit": PLANS[plan_tier].get_limit("max_clientes"),
                    "percentage": usage.get_usage_percentage(plan_tier, "clientes"),
                },
                "atendimentos": {
                    "current": usage.metrics["atendimentos"],
                    "limit": PLANS[plan_tier].get_limit("max_atendimentos"),
                    "percentage": usage.get_usage_percentage(plan_tier, "atendimentos"),
                },
            }
        },
        message="Estatísticas de uso"
    )


@router.post("/webhook/stripe")
async def handle_stripe_webhook(payload: dict):
    """
    Webhook para receber eventos do Stripe
    - payment.succeeded
    - customer.subscription.updated
    - customer.subscription.deleted
    
    Em produção:
    - Validar assinatura do webhook (Stripe signing secret)
    - Processar diferentes tipos de eventos
    - Atualizar status no banco de dados
    """
    event_type = payload.get("type")
    
    if event_type == "payment_intent.succeeded":
        logger.info(f"Payment succeeded: {payload.get('id')}")
        # TODO: Atualizar status de pagamento
    
    elif event_type == "customer.subscription.updated":
        logger.info(f"Subscription updated: {payload.get('id')}")
        # TODO: Atualizar plano
    
    elif event_type == "customer.subscription.deleted":
        logger.info(f"Subscription deleted: {payload.get('id')}")
        # TODO: Desativar subscription
    
    return success_response(data={}, message="Webhook recebido")


@router.post("/estimate-upgrade")
async def estimate_upgrade_cost(
    empresa_id: int,
    new_tier: str,
    days_in_current_cycle: int = 15,
):
    """
    Estima custo for pro-rata upgrade
    Útil para mostrar ao usuário quanto vai pagar
    """
    try:
        new_plan_tier = PlanTier(new_tier)
    except ValueError:
        raise NotFoundError(f"Plano '{new_tier}' inválido")
    
    # Calcula pro-rata para upgrade mid-cycle
    pro_rata = BillingCycle.calculate_pro_rata(
        new_plan_tier,
        days_used=15,
        total_days=30
    )
    
    full_price = PLANS[new_plan_tier].price_monthly
    current_plan = "pro"  # TODO: buscar do banco
    current_credit = PLANS[PlanTier(current_plan)].price_monthly * (15/30)
    
    return success_response(
        data={
            "empresa_id": empresa_id,
            "from_plan": current_plan,
            "to_plan": new_tier,
            "current_monthly": PLANS[PlanTier(current_plan)].price_monthly,
            "new_monthly": PLANS[new_plan_tier].price_monthly,
            "current_credit": round(current_credit, 2),
            "pro_rata_charge": round(pro_rata - current_credit, 2),
            "total_charge": round(pro_rata, 2),
            "next_billing_amount": PLANS[new_plan_tier].price_monthly,
        },
        message="Estimativa de custo do upgrade"
    )
