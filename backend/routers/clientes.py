from fastapi import APIRouter, Depends, HTTPException, status
from backend.schemas import ClienteCreate, ClienteOut
from backend import models, database
from backend.dependencies import require_authenticated_empresa
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/api/clientes", tags=["clientes"])

@router.get("", response_model=List[ClienteOut])
def listar_clientes(
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db)
):
    clientes = db.query(models.Cliente).filter(models.Cliente.empresa_id == empresa.id).order_by(models.Cliente.data_primeiro_contato.desc()).all()
    return clientes

@router.post("", status_code=status.HTTP_201_CREATED)
def criar_cliente(
    cliente: ClienteCreate,
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db)
):
    existente = db.query(models.Cliente).filter(
        models.Cliente.empresa_id == empresa.id,
        models.Cliente.telefone == cliente.telefone
    ).first()
    if existente:
        raise HTTPException(status_code=400, detail="Cliente já cadastrado com este telefone.")
    novo_cliente = models.Cliente(
        empresa_id=empresa.id,
        nome=cliente.nome,
        telefone=cliente.telefone,
        anotacoes_rapidas=cliente.anotacoes_rapidas
    )
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente
