from fastapi import APIRouter, Depends, Query
from backend import models, database
from backend.dependencies import require_authenticated_empresa, get_tenant_db
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
import logging

logger = logging.getLogger("clientflow.dashboard")

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def obter_dashboard(
    period: str = Query("30d"),
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(get_tenant_db)
):
    """
    Retorna estatísticas do dashboard filtradas por empresa
    """
    logger.info("Dashboard requisitado para empresa ID=%s (%s)", empresa.id, empresa.nome_empresa)
    
    # Total de clientes
    total_clientes = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id
    ).count()
    
    # Total de clientes ativos (com pelo menos um atendimento)
    total_clientes_ativos = db.query(func.count(func.distinct(models.Atendimento.cliente_id))).filter(
        models.Atendimento.empresa_id == empresa.id
    ).scalar() or 0
    
    # Total de atendimentos
    total_atendimentos = db.query(models.Atendimento).filter(
        models.Atendimento.empresa_id == empresa.id
    ).count()
    
    # Top clientes (clientes com mais atendimentos)
    top_clientes_data = db.query(
        models.Cliente.id,
        models.Cliente.nome,
        func.count(models.Atendimento.id).label('total_atendimentos')
    ).join(
        models.Atendimento, models.Atendimento.cliente_id == models.Cliente.id
    ).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Atendimento.empresa_id == empresa.id
    ).group_by(
        models.Cliente.id, models.Cliente.nome
    ).order_by(
        desc('total_atendimentos')
    ).limit(5).all()
    
    top_clientes = [
        {
            "id": cliente.id,
            "nome": cliente.nome,
            "total_atendimentos": cliente.total_atendimentos
        }
        for cliente in top_clientes_data
    ]
    
    logger.info(
        "Dashboard para empresa %s: %d clientes, %d ativos, %d atendimentos, %d top clientes",
        empresa.id, total_clientes, total_clientes_ativos, total_atendimentos, len(top_clientes)
    )
    
    return {
        "estatisticas": {
            "total_clientes": total_clientes,
            "total_clientes_ativos": total_clientes_ativos,
            "total_atendimentos": total_atendimentos
        },
        "top_clientes": top_clientes
    }
