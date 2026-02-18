"""
Clientes Router - Client management endpoints
"""

from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.schemas import ClienteCreate
from backend import models, database
from backend.dependencies import require_authenticated_empresa
from backend.exceptions import NotFoundError, ConflictError, ValidationError
from backend.responses import success_response, paginated_response
from backend.validators import ClientNameValidator, PhoneValidator
from backend.utils import log_action, log_error, get_logger
from backend.performance import PaginationOptimizer

logger = get_logger("clientflow.routers.clientes")

router = APIRouter(prefix="/api/clientes", tags=["Clients"])


# ========== LISTAR CLIENTES ==========

@router.get(
    "",
    summary="Listar todos os clientes",
    description="Retorna lista paginada de clientes da empresa autenticada"
)
def listar_clientes(
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
    skip: int = Query(0, ge=0, description="Número de itens a pular"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de itens"),
    ordenar_por: str = Query("data", regex="^(nome|telefone|data)$", description="Campo para ordenação"),
):
    """
    Listar clientes da empresa com paginação.
    
    - Isolado por tenant (só mostra clientes da empresa autenticada)
    - Paginação automática
    - Ordenação configurável
    
    **Query Parameters:**
    - `skip`: Offset para paginação (default: 0)
    - `limit`: Quantidade de itens (default: 20, max: 100)
    - `ordenar_por`: Campo de ordenação (nome, telefone, data)
    """
    try:
        # Validar paginação
        skip, limit = PaginationOptimizer.validate_pagination(skip, limit)

        # Contar total
        total = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        ).count()
        
        # Query com ordenação
        query = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        )
        
        if ordenar_por == "nome":
            query = query.order_by(models.Cliente.nome)
        elif ordenar_por == "telefone":
            query = query.order_by(models.Cliente.telefone)
        else:  # data padrão
            query = query.order_by(models.Cliente.data_primeiro_contato.desc())
        
        clientes = query.offset(skip).limit(limit).all()
        
        log_action(
            action="list",
            entity="cliente",
            usuario_id=empresa.id,
            details={"total": total, "returned": len(clientes)}
        )
        
        page = skip // limit + 1 if limit > 0 else 1
        return paginated_response(
            data=clientes,
            page=page,
            page_size=limit,
            total_items=total,
            message=f"{len(clientes)} clientes encontrados"
        )
        
    except Exception as e:
        log_error(e, context="Listar clientes", user_id=empresa.id)
        raise


# ========== OBTER CLIENTE ==========

@router.get(
    "/{cliente_id}",
    summary="Obter cliente específico",
    description="Retorna detalhes de um cliente específico"
)
def obter_cliente(
    cliente_id: int,
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
):
    """
    Obter cliente específico por ID.
    
    - Valida que o cliente pertence à empresa autenticada
    - Multi-tenant safe
    """
    try:
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == empresa.id
        ).first()
        
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)
        
        log_action(
            action="read",
            entity="cliente",
            entity_id=cliente_id,
            usuario_id=empresa.id
        )
        
        return success_response(
            data=cliente,
            message=f"Cliente '{cliente.nome}' encontrado"
        )
        
    except NotFoundError:
        raise
    except Exception as e:
        log_error(e, context="Obter cliente", user_id=empresa.id)
        raise


# ========== CRIAR CLIENTE ==========

@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Criar novo cliente",
    description="Registra um novo cliente para a empresa"
)
def criar_cliente(
    cliente: ClienteCreate,
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
):
    """
    Criar novo cliente.
    
    - Validação de nome e telefone
    - Verifica limite de clientes do plano
    - Evita duplicatas por telefone
    - Auditoria automática
    
    **Limits:**
    - Free: 100 clientes
    - Pro: 1000 clientes
    - Enterprise: Unlimited
    """
    try:
        # Validar nome
        nome_validado = ClientNameValidator.validate(cliente.nome)
        
        # Validar e normalizar telefone
        telefone_validado = PhoneValidator.validate(cliente.telefone) if cliente.telefone else None
        
        # Verificar limite de clientes
        contador_clientes = db.query(models.Cliente).filter(
            models.Cliente.empresa_id == empresa.id
        ).count()
        
        limite = empresa.limite_clientes or 1000
        if contador_clientes >= limite:
            raise ValidationError(
                f"Limite de clientes atingido ({limite})",
                field="clientes",
                details={"limit": limite, "current": contador_clientes}
            )
        
        # Verificar duplicata por telefone
        if telefone_validado:
            existente = db.query(models.Cliente).filter(
                models.Cliente.empresa_id == empresa.id,
                models.Cliente.telefone == telefone_validado
            ).first()
            
            if existente:
                raise ConflictError(
                    f"Cliente com telefone '{telefone_validado}' já existe",
                    resource="Cliente",
                    details={"telefone": telefone_validado, "cliente_id": existente.id}
                )
        
        # Criar cliente
        novo_cliente = models.Cliente(
            empresa_id=empresa.id,
            nome=nome_validado,
            telefone=telefone_validado,
            anotacoes_rapidas=cliente.anotacoes_rapidas or "",
        )
        
        db.add(novo_cliente)
        db.commit()
        db.refresh(novo_cliente)
        
        log_action(
            action="create",
            entity="cliente",
            entity_id=novo_cliente.id,
            usuario_id=empresa.id,
            details={"nome": novo_cliente.nome, "telefone": novo_cliente.telefone}
        )
        
        return success_response(
            data=novo_cliente,
            message=f"Cliente '{novo_cliente.nome}' criado com sucesso",
            status="success"
        )
        
    except (ValidationError, ConflictError) as e:
        logger.warning(f"Falha ao criar cliente: {e.message}")
        raise
    except Exception as e:
        log_error(e, context="Criar cliente", user_id=empresa.id)
        raise


# ========== ATUALIZAR CLIENTE ==========

@router.put(
    "/{cliente_id}",
    summary="Atualizar cliente",
    description="Atualiza dados do cliente"
)
def atualizar_cliente(
    cliente_id: int,
    cliente_update: ClienteCreate,
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
):
    """
    Atualizar cliente.
    
    - Validação de campos
    - Multi-tenant safe
    - Auditoria de mudanças
    """
    try:
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == empresa.id
        ).first()
        
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)
        
        # Validar
        nome_validado = ClientNameValidator.validate(cliente_update.nome)
        telefone_validado = PhoneValidator.validate(cliente_update.telefone) if cliente_update.telefone else None
        
        # Atualizar
        cliente.nome = nome_validado
        cliente.telefone = telefone_validado
        cliente.anotacoes_rapidas = cliente_update.anotacoes_rapidas or ""
        
        db.commit()
        db.refresh(cliente)
        
        log_action(
            action="update",
            entity="cliente",
            entity_id=cliente_id,
            usuario_id=empresa.id,
            details={"nome": cliente.nome}
        )
        
        return success_response(
            data=cliente,
            message="Cliente atualizado com sucesso"
        )
        
    except (NotFoundError, ValidationError) as e:
        raise
    except Exception as e:
        log_error(e, context="Atualizar cliente", user_id=empresa.id)
        raise


# ========== DELETAR CLIENTE ==========

@router.delete(
    "/{cliente_id}",
    status_code=status.HTTP_200_OK,
    summary="Deletar cliente",
    description="Remove um cliente do sistema"
)
def deletar_cliente(
    cliente_id: int,
    empresa: models.Empresa = Depends(require_authenticated_empresa),
    db: Session = Depends(database.get_db),
):
    """
    Deletar cliente.
    
    - Remove atendimentos relacionados
    - Multi-tenant safe
    - Auditoria de deleção
    """
    try:
        cliente = db.query(models.Cliente).filter(
            models.Cliente.id == cliente_id,
            models.Cliente.empresa_id == empresa.id
        ).first()
        
        if not cliente:
            raise NotFoundError("Cliente", cliente_id)
        
        nome_cliente = cliente.nome
        
        # Deletar (cascade automático)
        db.delete(cliente)
        db.commit()
        
        log_action(
            action="delete",
            entity="cliente",
            entity_id=cliente_id,
            usuario_id=empresa.id,
            details={"nome": nome_cliente}
        )
        
        return success_response(
            message=f"Cliente '{nome_cliente}' deletado com sucesso"
        )
        
    except NotFoundError:
        raise
    except Exception as e:
        log_error(e, context="Deletar cliente", user_id=empresa.id)
        raise

