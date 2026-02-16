from fastapi import APIRouter, Depends, Query
from backend import models, database
from sqlalchemy.orm import Session
from typing import Optional

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def obter_dashboard(
    token: Optional[str] = Query(None),
    empresa: models.Empresa = Depends(database.get_db),
    db: Session = Depends(database.get_db)
):
    total_clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa.id).count()
    total_atendimentos = db.query(models.Atendimento).filter(models.Atendimento.empresa_id == empresa.id).count()
    return {
        "total_clientes": total_clientes,
        "total_atendimentos": total_atendimentos
    }
