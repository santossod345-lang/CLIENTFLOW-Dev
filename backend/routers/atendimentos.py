from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend import database, models
from backend.dependencies import require_authenticated_empresa
from backend.plan_limits import check_plan_limits
from pydantic import BaseModel, Field


class AtendimentoCreateApi(BaseModel):
    cliente_id: int = Field(..., ge=1)
    tipo_servico: str = Field(..., min_length=2, max_length=100)
    descricao_servico: str = Field(default="", max_length=2000)
    meses_retorno: int | None = Field(default=None, ge=0, le=120)


router = APIRouter(prefix="/api/atendimentos", tags=["atendimentos"])


@router.get("", response_model=List[dict])
def listar_atendimentos(
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
):
    atendimentos = (
        db.query(models.Atendimento)
        .filter(models.Atendimento.empresa_id == empresa.id)
        .order_by(models.Atendimento.data_atendimento.desc())
        .all()
    )

    # Minimal shape to keep frontend compatibility without adding new schemas.
    return [
        {
            "id": a.id,
            "empresa_id": a.empresa_id,
            "cliente_id": a.cliente_id,
            "tipo_servico": a.tipo_servico,
            "status_atendimento": a.status_atendimento,
            "descricao_servico": a.descricao_servico,
            "meses_retorno": a.meses_retorno,
            "data_atendimento": a.data_atendimento,
        }
        for a in atendimentos
    ]


@router.post("", status_code=status.HTTP_201_CREATED)
def criar_atendimento(
    body: AtendimentoCreateApi,
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
):
    # Ensure client belongs to this empresa.
    cliente = (
        db.query(models.Cliente)
        .filter(models.Cliente.id == body.cliente_id, models.Cliente.empresa_id == empresa.id)
        .first()
    )
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    check_plan_limits(empresa, "atendimentos", db=db)

    atendimento = models.Atendimento(
        empresa_id=empresa.id,
        cliente_id=body.cliente_id,
        tipo_servico=body.tipo_servico,
        descricao_servico=body.descricao_servico,
        meses_retorno=body.meses_retorno,
    )
    db.add(atendimento)
    db.commit()
    db.refresh(atendimento)
    return atendimento
