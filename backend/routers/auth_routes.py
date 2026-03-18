import logging
import time
from collections import defaultdict, deque

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend import auth, database, models
from backend.dependencies import require_authenticated_empresa
from backend.schemas import EmpresaCreate, EmpresaLogin, EmpresaOut, RefreshRequest, TokenResponse

logger = logging.getLogger('clientflow.auth_routes')

router = APIRouter(prefix='/api/auth', tags=['auth'])
public_router = APIRouter(prefix='/auth', tags=['auth'])

# Lightweight in-memory limiter. In multi-instance setups, replace with Redis-based limiter.
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


def _register_company(payload: EmpresaCreate, db: Session) -> models.Empresa:
    existing = db.query(models.Empresa).filter(models.Empresa.email_login == payload.email_login).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email ja cadastrado')

    company = models.Empresa(
        nome_empresa=payload.nome_empresa,
        nicho=payload.nicho,
        telefone=payload.telefone,
        email_login=payload.email_login,
        senha_hash=auth.get_password_hash(payload.senha),
    )
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


def _login_company(payload: EmpresaLogin, db: Session) -> TokenResponse:
    company = db.query(models.Empresa).filter(models.Empresa.email_login == payload.email_login).first()
    if not company or not auth.verify_password(payload.senha, company.senha_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email ou senha incorretos')

    access_token = auth.create_access_token({'sub': company.id})
    refresh_token = auth.create_refresh_token(db, company.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token, token_type='bearer')


def _refresh_tokens(payload: RefreshRequest, db: Session) -> TokenResponse:
    existing = auth.verify_refresh_token(db, payload.refresh_token)
    if not existing:
        raise HTTPException(status_code=401, detail='Refresh token invalido ou expirado')

    new_raw = auth.create_session_token()
    ok, new_token = auth.rotate_refresh_token(db, existing.jti, new_raw)
    if not ok or not new_token:
        raise HTTPException(status_code=500, detail='Unable to rotate refresh token')

    access_token = auth.create_access_token({'sub': existing.empresa_id})
    return TokenResponse(access_token=access_token, refresh_token=new_token, token_type='bearer')


@router.post('/register', response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
@public_router.post('/register', response_model=EmpresaOut, status_code=status.HTTP_201_CREATED)
def register_company(payload: EmpresaCreate, db: Session = Depends(database.get_db)):
    try:
        return _register_company(payload, db)
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception('Database error while registering company')
        raise HTTPException(status_code=503, detail='Banco indisponivel. Tente novamente em instantes.')


@router.post('/login', response_model=TokenResponse)
@public_router.post('/login', response_model=TokenResponse)
def login_company(payload: EmpresaLogin, request: Request, db: Session = Depends(database.get_db)):
    _enforce_login_rate_limit(request, payload.email_login)

    try:
        return _login_company(payload, db)
    except HTTPException:
        raise
    except SQLAlchemyError:
        db.rollback()
        logger.exception('Database error while logging in')
        raise HTTPException(status_code=503, detail='Banco indisponivel. Tente novamente em instantes.')


@router.post('/refresh', response_model=TokenResponse)
@public_router.post('/refresh', response_model=TokenResponse)
def refresh_auth_token(payload: RefreshRequest, db: Session = Depends(database.get_db)):
    return _refresh_tokens(payload, db)


@router.get('/me', response_model=EmpresaOut)
@public_router.get('/me', response_model=EmpresaOut)
def get_me(company: models.Empresa = Depends(require_authenticated_empresa)):
    return company
