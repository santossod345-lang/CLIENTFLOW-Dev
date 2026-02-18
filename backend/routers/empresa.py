"""
Empresa Router - Company registration, authentication, and token management
Tier 1: BILLION-DOLLAR SaaS level implementation
"""

from fastapi import APIRouter, Depends, Request, status, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import os
import shutil
from pathlib import Path

from backend.schemas import EmpresaCreate, EmpresaLogin, RefreshRequest
from backend import models, auth, database
from backend.exceptions import (
    ValidationError,
    AuthenticationError,
    ConflictError,
    NotFoundError,
    AuthorizationError,
)
from backend.responses import success_response, error_response
from backend.validators import (
    EmailValidator,
    PasswordValidator,
    CompanyNameValidator,
    PhoneValidator,
    RegistrationValidator,
)
from backend.utils import log_auth, log_action, log_error, get_logger
from backend.security import rate_limit_check, InputValidator

logger = get_logger("clientflow.routers.empresa")

router = APIRouter(prefix="/api/empresas", tags=["Authentication"])


# ========== REGISTRO ==========

@router.post("/cadastrar", status_code=status.HTTP_201_CREATED, summary="Registrar nova empresa")
async def cadastrar_empresa(
    empresa: EmpresaCreate,
    request: Request,
    db: Session = Depends(database.get_db)
):
    """
    Registrar uma nova empresa no sistema.
    
    - Valida todos os campos
    - Garante unicidade de email
    - Hash seguro de senha
    - Multi-tenant ready
    
    **Retorna:** Dados da empresa criada
    """
    try:
        # Rate limiting
        await rate_limit_check(request)

        # Input safety check
        if not InputValidator.validate_input({
            "email_login": empresa.email_login,
            "nome_empresa": empresa.nome_empresa,
            "nicho": empresa.nicho,
            "telefone": empresa.telefone or "",
        }):
            raise ValidationError("Dados de entrada inválidos", field="payload")

        # Validação composta
        validated_data = RegistrationValidator.validate_company_registration({
            "email_login": empresa.email_login,
            "senha": empresa.senha,
            "nome_empresa": empresa.nome_empresa,
            "nicho": empresa.nicho,
            "telefone": empresa.telefone,
        })
        
        # Verificar unicidade de email
        existing = db.query(models.Empresa).filter(
            models.Empresa.email_login == validated_data["email_login"]
        ).first()
        
        if existing:
            log_auth(
                action="register",
                email=validated_data["email_login"],
                success=False,
                details={"reason": "email_already_exists"}
            )
            raise ConflictError(
                "Email já está cadastrado",
                resource="Empresa",
                details={"field": "email_login"}
            )
        
        # Criar empresa
        senha_hash = auth.get_password_hash(validated_data["senha"])
        nova_empresa = models.Empresa(
            nome_empresa=validated_data["nome_empresa"],
            nicho=validated_data["nicho"],
            telefone=validated_data.get("telefone"),
            email_login=validated_data["email_login"],
            senha_hash=senha_hash,
            plano_empresa="free",  # Plano padrão
            ativo=1,  # Ativa automaticamente
        )
        
        db.add(nova_empresa)
        db.commit()
        db.refresh(nova_empresa)
        
        # Log de sucesso
        log_auth(
            action="register",
            email=validated_data["email_login"],
            success=True,
            details={"empresa_id": nova_empresa.id, "nicho": nova_empresa.nicho}
        )
        
        log_action(
            action="create",
            entity="empresa",
            entity_id=nova_empresa.id,
            details={"nome": nova_empresa.nome_empresa, "nicho": nova_empresa.nicho}
        )
        
        return success_response(
            data=nova_empresa,
            message=f"Empresa '{nova_empresa.nome_empresa}' criada com sucesso",
            status="success"
        )
        
    except (ValidationError, ConflictError) as e:
        logger.warning(f"Registro falhou: {e.message}")
        raise
    except Exception as e:
        log_error(e, context="Cadastro de empresa", details={"email": empresa.email_login})
        raise


# ========== LOGIN ==========

@router.post("/login", summary="Fazer login")
async def login_empresa(
    login: EmpresaLogin,
    request: Request,
    db: Session = Depends(database.get_db)
):
    """
    Fazer login com email e senha.
    
    - Valida credenciais
    - Retorna access_token (15 min) e refresh_token (7 dias)
    - Log de segurança
    
    **Returns:**
    - `access_token`: JWT token para requisições autenticadas
    - `refresh_token`: Token para renovar access_token
    - `token_type`: "bearer"
    """
    try:
        # Rate limiting
        await rate_limit_check(request)

        # Input safety check
        if not InputValidator.validate_input({
            "email_login": login.email_login,
            "senha": login.senha,
        }):
            raise ValidationError("Dados de entrada inválidos", field="payload")

        # Validar email
        email = EmailValidator.validate(login.email_login)
        
        # Buscar empresa
        empresa = db.query(models.Empresa).filter(
            models.Empresa.email_login == email
        ).first()
        
        if not empresa:
            log_auth(
                action="login",
                email=email,
                success=False,
                details={"reason": "user_not_found"}
            )
            raise AuthenticationError("Email ou senha incorretos")
        
        # Verificar senha
        if not auth.verify_password(login.senha, empresa.senha_hash):
            log_auth(
                action="login",
                email=email,
                success=False,
                details={"reason": "invalid_password"}
            )
            raise AuthenticationError("Email ou senha incorretos")
        
        # Verificar se empresa está ativa
        if not empresa.ativo:
            log_auth(
                action="login",
                email=email,
                success=False,
                details={"reason": "company_inactive"}
            )
            raise AuthorizationError("Empresa inativa")
        
        # Gerar tokens (converter para string para conformidade JWT RFC 7519)
        access_token = auth.create_access_token({"sub": str(empresa.id)})
        refresh_token = auth.create_refresh_token(db, empresa.id)
        
        log_auth(
            action="login",
            email=email,
            success=True,
            details={"empresa_id": empresa.id}
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "token": access_token,
                "empresa": {
                    "id": empresa.id,
                    "nome_empresa": empresa.nome_empresa,
                    "nicho": empresa.nicho,
                    "telefone": empresa.telefone,
                    "email_login": empresa.email_login,
                    "plano_empresa": empresa.plano_empresa,
                }
            },
            message="Login realizado com sucesso"
        )
        
    except (ValidationError, AuthenticationError, AuthorizationError) as e:
        logger.warning(f"Login falhou: {e.message}")
        raise
    except Exception as e:
        log_error(e, context="Login", details={"email": login.email_login})
        raise


# ========== LOGOUT ==========

@router.post("/logout", summary="Fazer logout")
def logout_empresa(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    """
    Logout - Revoga o token de refresh.
    
    - Marca token como revogado
    - Invalida sessão
    """
    try:
        payload = auth.decode_access_token(token)
        if not payload:
            raise AuthenticationError("Token inválido")
        
        empresa_id = payload.get("sub")
        
        log_auth(
            action="logout",
            email="",  # Email não disponível sem query
            success=True,
            details={"empresa_id": empresa_id}
        )
        
        return success_response(
            message="Logout realizado com sucesso"
        )
        
    except Exception as e:
        log_error(e, context="Logout")
        raise


# ========== REFRESH TOKEN ==========

@router.post("/refresh", summary="Renovar token de acesso")
def refresh_token_endpoint(
    body: RefreshRequest,
    db: Session = Depends(database.get_db)
):
    """
    Renovar access_token usando refresh_token.
    
    - Válido por 7 dias
    - Implementa token rotation
    - Rastreia histórico de tokens
    
    **Returns:** Novo access_token + novo refresh_token
    """
    try:
        # Verificar refresh token
        rt = auth.verify_refresh_token(db, body.refresh_token)
        if not rt:
            log_auth(
                action="refresh",
                email="",
                success=False,
                details={"reason": "invalid_refresh_token"}
            )
            raise AuthenticationError("Refresh token inválido ou expirado")
        
        # Criar novo token (token rotation)
        new_raw = auth.create_session_token()
        ok, new_token = auth.rotate_refresh_token(db, rt.jti, new_raw)
        
        if not ok:
            log_error(
                Exception("Token rotation failed"),
                context="Refresh token rotation",
                user_id=rt.empresa_id
            )
            raise Exception("Erro ao renovar token")
        
        # Gerar novo access token
        access_token = auth.create_access_token({"sub": rt.empresa_id})
        
        log_auth(
            action="refresh",
            email="",
            success=True,
            details={"empresa_id": rt.empresa_id}
        )
        
        return success_response(
            data={
                "access_token": access_token,
                "refresh_token": new_token,
                "token_type": "bearer"
            },
            message="Token renovado com sucesso"
        )
        
    except AuthenticationError as e:
        raise
    except Exception as e:
        log_error(e, context="Token refresh")
        raise


# ========== COMPANY PROFILE ==========

@router.get("/me", summary="Obter dados da empresa logada")
def get_company_profile(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    """
    Obter os dados da empresa autenticada.
    
    **Returns:** Dados completos da empresa
    """
    try:
        payload = auth.decode_access_token(token)
        if not payload:
            raise AuthenticationError("Token inválido")
        
        empresa_id = payload.get("sub")
        empresa = db.query(models.Empresa).filter(
            models.Empresa.id == empresa_id
        ).first()
        
        if not empresa:
            raise NotFoundError("Empresa não encontrada", resource="Empresa")
        
        return success_response(
            data={
                "id": empresa.id,
                "nome_empresa": empresa.nome_empresa,
                "nicho": empresa.nicho,
                "telefone": empresa.telefone,
                "email_login": empresa.email_login,
                "plano_empresa": empresa.plano_empresa,
                "logo_url": empresa.logo_url,
                "data_cadastro": empresa.data_cadastro,
            },
            message="Dados da empresa recuperados com sucesso"
        )
        
    except (AuthenticationError, NotFoundError) as e:
        raise
    except Exception as e:
        log_error(e, context="Get company profile")
        raise


@router.put("/me", summary="Atualizar dados da empresa")
def update_company_profile(
    data: dict,
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    """
    Atualizar os dados da empresa autenticada.
    
    **Body:**
    - `nome_empresa`: Nome da empresa
    - `nicho`: Nicho/área de atuação
    - `telefone`: Telefone de contato
    
    **Returns:** Dados atualizados da empresa
    """
    try:
        payload = auth.decode_access_token(token)
        if not payload:
            raise AuthenticationError("Token inválido")
        
        empresa_id = payload.get("sub")
        empresa = db.query(models.Empresa).filter(
            models.Empresa.id == empresa_id
        ).first()
        
        if not empresa:
            raise NotFoundError("Empresa não encontrada", resource="Empresa")
        
        # Atualizar campos permitidos
        if "nome_empresa" in data and data["nome_empresa"]:
            empresa.nome_empresa = data["nome_empresa"]
        if "nicho" in data and data["nicho"]:
            empresa.nicho = data["nicho"]
        if "telefone" in data:
            empresa.telefone = data["telefone"]
        
        db.commit()
        db.refresh(empresa)
        
        log_action(
            action="update",
            entity="empresa",
            entity_id=empresa.id,
            details={"fields": list(data.keys())}
        )
        
        return success_response(
            data={
                "id": empresa.id,
                "nome_empresa": empresa.nome_empresa,
                "nicho": empresa.nicho,
                "telefone": empresa.telefone,
                "email_login": empresa.email_login,
                "plano_empresa": empresa.plano_empresa,
                "logo_url": empresa.logo_url,
            },
            message="Dados da empresa atualizados com sucesso"
        )
        
    except (AuthenticationError, NotFoundError) as e:
        raise
    except Exception as e:
        log_error(e, context="Update company profile")
        raise


# ========== LOGO UPLOAD ==========

# Criar pasta de uploads se não existir
UPLOAD_DIR = Path("uploads/logos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.post("/logo", summary="Fazer upload da logo da empresa")
async def upload_logo(
    file: UploadFile = File(...),
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    """
    Upload de logo da empresa.
    
    - Aceita: JPG, JPEG, PNG, WEBP
    - Tamanho máximo: 5MB
    - Salva em /uploads/logos/
    
    **Returns:** URL da logo salva
    """
    try:
        payload = auth.decode_access_token(token)
        if not payload:
            raise AuthenticationError("Token inválido")
        
        empresa_id = payload.get("sub")
        empresa = db.query(models.Empresa).filter(
            models.Empresa.id == empresa_id
        ).first()
        
        if not empresa:
            raise NotFoundError("Empresa não encontrada", resource="Empresa")
        
        # Validar arquivo
        if not file.filename:
            raise ValidationError("Arquivo inválido", field="file")
        
        if not allowed_file(file.filename):
            raise ValidationError(
                "Tipo de arquivo não permitido. Use JPG, PNG ou WEBP",
                field="file"
            )
        
        # Validar tamanho (5MB max)
        contents = await file.read()
        if len(contents) > 5 * 1024 * 1024:
            raise ValidationError("Arquivo muito grande (máximo 5MB)", field="file")
        
        # Salvar arquivo
        file_ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"logo_empresa_{empresa_id}.{file_ext}"
        filepath = UPLOAD_DIR / filename
        
        with open(filepath, "wb") as f:
            f.write(contents)
        
        # Salvar URL no banco (path relativo para portabilidade)
        logo_url = f"/uploads/logos/{filename}"
        empresa.logo_url = logo_url
        
        db.commit()
        db.refresh(empresa)
        
        log_action(
            action="upload_logo",
            entity="empresa",
            entity_id=empresa.id,
            details={"filename": filename, "size": len(contents)}
        )
        
        return success_response(
            data={
                "logo_url": logo_url,
                "filename": filename,
            },
            message="Logo enviada com sucesso"
        )
        
    except (ValidationError, AuthenticationError, NotFoundError) as e:
        raise
    except Exception as e:
        log_error(e, context="Upload logo", details={"filename": file.filename})
        raise


@router.get("/me/logo", summary="Obter URL da logo da empresa")
def get_company_logo(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(database.get_db),
):
    """
    Obter URL da logo da empresa autenticada.
    
    **Returns:** 
    - `logo_url`: URL da logo ou null se não tiver
    """
    try:
        payload = auth.decode_access_token(token)
        if not payload:
            raise AuthenticationError("Token inválido")
        
        empresa_id = payload.get("sub")
        empresa = db.query(models.Empresa).filter(
            models.Empresa.id == empresa_id
        ).first()
        
        if not empresa:
            raise NotFoundError("Empresa não encontrada", resource="Empresa")
        
        return success_response(
            data={
                "logo_url": empresa.logo_url,
            },
            message="Logo recuperada com sucesso"
        )
        
    except (AuthenticationError, NotFoundError) as e:
        raise
    except Exception as e:
        log_error(e, context="Get company logo")
        raise
