import logging
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend import auth, database, models
from backend.dependencies import require_authenticated_empresa
from backend.schemas import EmpresaCreate, EmpresaLogin, EmpresaOut, RefreshRequest, TokenResponse

logger = logging.getLogger("clientflow.empresa")

router = APIRouter(prefix="/api/empresas", tags=["empresas"])

_login_attempts = defaultdict(lambda: deque(maxlen=30))
MAX_LOGIN_ATTEMPTS = 5
LOGIN_WINDOW_SECONDS = 60


def _enforce_login_rate_limit(request: Request, email: str) -> None:
    ip = request.client.host if request.client else 'unknown'
    key = f'{ip}:{email.lower().strip()}'
    now = time.time()
    attempts = _login_attempts[key]

    while attempts and now - attempts[0] > LOGIN_WINDOW_SECONDS:
        attempts.popleft()

    if len(attempts) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(status_code=429, detail='Muitas tentativas de login. Tente novamente em instantes.')

    attempts.append(now)


@router.get("/me", response_model=EmpresaOut)
def obter_empresa_atual(empresa: models.Empresa = Depends(require_authenticated_empresa)):
    return empresa


@router.post("/cadastrar", response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def cadastrar_empresa(empresa: EmpresaCreate, db: Session = Depends(database.get_db)):
    try:
        existing = db.query(models.Empresa).filter(models.Empresa.email_login == empresa.email_login).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email ja cadastrado")

        senha_hash = auth.get_password_hash(empresa.senha)
        nova_empresa = models.Empresa(
            nome_empresa=empresa.nome_empresa,
            nicho=empresa.nicho,
            telefone=empresa.telefone,
            email_login=empresa.email_login,
            senha_hash=senha_hash,
        )
        db.add(nova_empresa)
        db.commit()
        db.refresh(nova_empresa)
        return nova_empresa
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while creating company")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco indisponivel ou esquema nao inicializado. Tente novamente em instantes.",
        )


@router.post("/login")
def login_empresa(login: EmpresaLogin, request: Request, db: Session = Depends(database.get_db)):
    _enforce_login_rate_limit(request, login.email_login)
    try:
        empresa = db.query(models.Empresa).filter(models.Empresa.email_login == login.email_login).first()
        if not empresa or not auth.verify_password(login.senha, empresa.senha_hash):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha incorretos")
        access_token = auth.create_access_token({"sub": empresa.id})
        refresh_token = auth.create_refresh_token(db, empresa.id)
        logger.info("Login bem-sucedido para empresa ID=%s (%s)", empresa.id, empresa.email_login)
        return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception("Database error while logging in")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Banco indisponivel ou esquema nao inicializado. Tente novamente em instantes.",
        )


@router.post("/logout")
def logout_empresa(token: str):
    # Implementar revogacao de sessao/refresh
    return {"detail": "Logout realizado"}


@router.post("/refresh", response_model=TokenResponse)
def refresh_token_endpoint(body: RefreshRequest, db: Session = Depends(database.get_db)):
    rt = auth.verify_refresh_token(db, body.refresh_token)
    if not rt:
        raise HTTPException(status_code=401, detail="Refresh token invalido ou expirado")
    new_raw = auth.create_session_token()
    ok, new_token = auth.rotate_refresh_token(db, rt.jti, new_raw)
    if not ok:
        raise HTTPException(status_code=500, detail="Unable to rotate refresh token")
    access_token = auth.create_access_token({"sub": rt.empresa_id})
    return {"access_token": access_token, "refresh_token": new_token, "token_type": "bearer"}

