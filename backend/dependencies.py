from fastapi import Depends, Request
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import auth, models
import logging

logger = logging.getLogger("clientflow.dependencies")

def require_authenticated_empresa(token: str = Depends(auth.oauth2_scheme), db: Session = Depends(get_db)) -> models.Empresa:
    logger.info("Token recebido: %s...", token[:20] if token else "VAZIO")
    empresa = auth.get_current_empresa_jwt(token, db)
    logger.info("Usuário autenticado: empresa %s (%s)", empresa.id, empresa.nome_empresa)
    return empresa


def get_tenant_db(request: Request, db: Session = Depends(get_db)):
    """Return a DB session with search_path set to the tenant schema derived from request.state.empresa_id.
    Falls back to public if not set."""
    from sqlalchemy import text
    schema = None
    if hasattr(request.state, "empresa_id") and request.state.empresa_id:
        schema = f"empresa_{request.state.empresa_id}"
    dialect = db.bind.dialect.name if db.bind is not None else ""
    if schema and dialect == "postgresql":
        db.execute(text(f"SET search_path TO {schema}, public"))
    yield db
