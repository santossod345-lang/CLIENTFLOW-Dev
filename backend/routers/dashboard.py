from fastapi import APIRouter, Depends
from backend import models, database
from backend.dependencies import require_authenticated_empresa
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

@router.get("")
def obter_dashboard(
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db)
):
    total_clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa.id).count()
    total_atendimentos = db.query(models.Atendimento).filter(models.Atendimento.empresa_id == empresa.id).count()
    return {
        "total_clientes": total_clientes,
        "total_atendimentos": total_atendimentos
    }
