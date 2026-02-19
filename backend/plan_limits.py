from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend import database, models


FREE_LIMIT_MESSAGE = "Você atingiu o limite do plano FREE."


def check_plan_limits(
    empresa: models.Empresa,
    resource_type: str,
    db: Optional[Session] = None,
) -> None:
    """Enforce plan limits for the authenticated empresa.

    Raises:
        HTTPException(403) when a FREE plan limit is reached.

    Notes:
        - Always filters by empresa_id.
        - Never trusts the frontend for limit values.
        - PRO is treated as unlimited.
    """

    if not empresa:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autenticado")

    plano = (empresa.plano_empresa or "free").strip().lower()

    # PRO is unlimited by definition.
    if plano == "pro":
        return

    if resource_type == "clientes":
        limit = empresa.limite_clientes
        model = models.Cliente
    elif resource_type == "atendimentos":
        limit = empresa.limite_atendimentos
        model = models.Atendimento
    else:
        raise HTTPException(status_code=400, detail="resource_type inválido")

    # Treat unset/invalid limits as unlimited.
    if limit is None or int(limit) <= 0:
        return

    close_db = False
    if db is None:
        db = database.SessionLocal()
        close_db = True

    try:
        total = db.query(model).filter(model.empresa_id == empresa.id).count()
        if total >= int(limit):
            if plano == "free":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=FREE_LIMIT_MESSAGE)
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Você atingiu o limite do seu plano.")
    finally:
        if close_db:
            db.close()
