"""
Dashboard Router - Analytics and business intelligence endpoints
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from backend import models, database
from backend.dependencies import require_authenticated_empresa
from backend.responses import success_response
from backend.utils import log_action, log_error, get_logger
from backend.performance import cache
from backend.monetization import FeatureGate, PlanTier
from backend.exceptions import AuthorizationError

logger = get_logger("clientflow.routers.dashboard")

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


# ========== DASHBOARD OVERVIEW ==========

@router.get(
    "",
    summary="Obter visão geral do dashboard",
    description="Retorna estatísticas e KPIs da empresa"
)
def obter_dashboard(
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
    periodo_dias: int = Query(30, ge=1, le=365, description="Período em dias para análise"),
) -> Dict[str, Any]:
    """
    Obter dashboard com KPIs e estatísticas da empresa.
    
    **Métricas incluídas:**
    - Total de clientes
    - Total de atendimentos
    - Atendimentos recentes
    - Top clientes (mais atendimentos)
    - Tempo médio de retorno
    - Clientes novos (período)
    - Taxa de atividade
    
    **Query Parameters:**
    - `periodo_dias`: Quantos dias para análise (default: 30)
    """
    try:
        cache_key = f"dashboard:{empresa.id}:{periodo_dias}"
        cached = cache.get(cache_key)
        if cached:
            return success_response(
                data=cached,
                message="Dashboard carregado do cache"
            )
        # ===== MÉTRICAS GERAIS =====
        total_clientes = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        ).count()
        
        total_atendimentos = db.query(models.Atendimento).filter(
            models.Atendimento.empresa_id == empresa.id
        ).count()
        
        # ===== ATENDIMENTOS RECENTES =====
        ultimos_atendimentos = db.query(
            models.Atendimento,
            models.Cliente.nome.label("cliente_nome")
        ).join(
            models.Cliente, models.Atendimento.cliente_id == models.Cliente.id
        ).filter(
            models.Atendimento.empresa_id == empresa.id
        ).order_by(models.Atendimento.data_atendimento.desc()).limit(10).all()
        
        atendimentos_recentes = [
            {
                "id": a.Atendimento.id,
                "cliente_nome": a.cliente_nome,
                "tipo_servico": a.Atendimento.tipo_servico,
                "data": a.Atendimento.data_atendimento.strftime("%d/%m/%Y %H:%M") if a.Atendimento.data_atendimento else None
            }
            for a in ultimos_atendimentos
        ]
        
        # ===== TOP CLIENTES =====
        top_clientes_query = db.query(
            models.Cliente.id,
            models.Cliente.nome,
            func.count(models.Atendimento.id).label("total_atendimentos")
        ).join(
            models.Atendimento, models.Cliente.id == models.Atendimento.cliente_id
        ).filter(
            models.Cliente.empresa_id == empresa.id
        ).group_by(
            models.Cliente.id, models.Cliente.nome
        ).order_by(
            func.count(models.Atendimento.id).desc()
        ).limit(5).all()
        
        top_clientes = [
            {
                "id": c.id,
                "nome": c.nome,
                "total_atendimentos": c.total_atendimentos
            }
            for c in top_clientes_query
        ]
        
        # ===== TEMPO MÉDIO DE RETORNO =====
        intervalos = []
        clientes_ids = db.query(models.Cliente.id).filter(
            models.Cliente.empresa_id == empresa.id
        ).all()
        
        for (cid,) in clientes_ids:
            atendimentos = db.query(models.Atendimento).filter(
                models.Atendimento.cliente_id == cid
            ).order_by(models.Atendimento.data_atendimento).all()
            
            datas = [a.data_atendimento for a in atendimentos if a.data_atendimento]
            if len(datas) > 1:
                for i in range(1, len(datas)):
                    diff = (datas[i] - datas[i-1]).days
                    if diff > 0:
                        intervalos.append(diff)
        
        tempo_medio_retorno = round(sum(intervalos) / len(intervalos), 1) if intervalos else None
        
        # ===== CLIENTES NOVOS (PERÍODO) =====
        data_limite = datetime.now() - timedelta(days=periodo_dias)
        clientes_novos = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id,
            models.Cliente.data_primeiro_contato >= data_limite
        ).count()
        
        # ===== TAXA DE ATIVIDADE =====
        atendimentos_periodo = db.query(models.Atendimento).filter(
            models.Atendimento.empresa_id == empresa.id,
            models.Atendimento.data_atendimento >= data_limite
        ).count()
        
        taxa_atividade = round((atendimentos_periodo / periodo_dias), 2) if periodo_dias > 0 else 0
        
        # Log
        log_action(
            action="view",
            entity="dashboard",
            usuario_id=empresa.id,
            details={"total_clientes": total_clientes, "total_atendimentos": total_atendimentos}
        )
        
        dashboard_data = {
            "empresa": {
                "id": empresa.id,
                "nome": empresa.nome_empresa,
                "nicho": empresa.nicho,
                "plano": empresa.plano_empresa,
            },
            "metricas": {
                "total_clientes": total_clientes,
                "total_atendimentos": total_atendimentos,
                "tempo_medio_retorno": tempo_medio_retorno,
                "clientes_novos_periodo": clientes_novos,
                "taxa_atividade_diaria": taxa_atividade,
            },
            "atendimentos_recentes": atendimentos_recentes,
            "top_clientes": top_clientes,
            "periodo_analise_dias": periodo_dias,
        }
        
        cache.set(cache_key, dashboard_data, ttl_seconds=60)

        return success_response(
            data=dashboard_data,
            message="Dashboard carregado com sucesso"
        )
        
    except Exception as e:
        log_error(e, context="Carregar dashboard", user_id=empresa.id)
        raise


# ========== ESTATÍSTICAS AVANÇADAS ==========

@router.get(
    "/stats/clientes",
    summary="Estatísticas de clientes",
    description="Análise detalhada de clientes"
)
def stats_clientes(
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
) -> Dict[str, Any]:
    """
    Estatísticas avançadas de clientes.
    
    **Retorna:**
    - Clientes por origem
    - Distribuição por cidade
    - Clientes ativos vs inativos
    """
    try:
        total = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        ).count()
        
        # Clientes com atendimentos (ativos)
        ativos = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        ).join(
            models.Atendimento,
            models.Cliente.id == models.Atendimento.cliente_id
        ).distinct().count()
        
        inativos = total - ativos
        
        stats = {
            "total": total,
            "ativos": ativos,
            "inativos": inativos,
            "taxa_atividade": round((ativos / total * 100), 1) if total > 0 else 0,
        }
        
        log_action(
            action="view",
            entity="stats_clientes",
            usuario_id=empresa.id
        )
        
        return success_response(
            data=stats,
            message="Estatísticas carregadas"
        )
        
    except Exception as e:
        log_error(e, context="Stats clientes", user_id=empresa.id)
        raise


# ========== EXPORTAÇÃO (Future Feature) ==========

@router.get(
    "/export/csv",
    summary="Exportar dados em CSV",
    description="[Premium feature] Exporta dados para CSV"
)
def export_csv(
    entidade: str = Query(..., regex="^(clientes|atendimentos)$", description="Que dados exportar"),
    empresa: models.Empresa = Depends(require_authenticated_empresa),
):
    """
    Exportar dados em CSV.
    
    **Features:**
    - Apenas para plano Premium+
    - Inclui auditoria de exportação
    - Rate limited
    
    **Status:** Feature em desenvolvimento
    """
    try:
        plan_name = (empresa.plano_empresa or "free").lower()
        try:
            plan_tier = PlanTier(plan_name)
        except ValueError:
            plan_tier = PlanTier.FREE

        if not FeatureGate.can_access(plan_tier, "csv_export"):
            raise AuthorizationError("Exportação CSV disponível apenas no plano Pro+")

        return success_response(
            message="Feature de exportação em desenvolvimento"
        )
    except Exception as e:
        log_error(e, context="Export CSV", user_id=empresa.id)
        raise

