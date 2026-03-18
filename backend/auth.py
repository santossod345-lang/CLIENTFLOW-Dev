from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from backend import models, database
from sqlalchemy.orm import Session
from typing import Optional, Tuple
from datetime import datetime, timedelta, timezone
import os
import hashlib
import uuid
import logging
# OAuth2 scheme para extrair o token do header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/empresas/login")
logger = logging.getLogger("clientflow.auth")
environment = os.getenv("ENVIRONMENT", "development").lower()
SECRET_KEY = os.getenv("JWT_SECRET") or os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or ""
if not SECRET_KEY:
    # Do not crash the service at import time; Railway will restart-loop and produce 502.
    # Generate an ephemeral key so the API can start, but log loudly so it gets fixed.
    SECRET_KEY = os.getenv("SECRET_KEY_RUNTIME", "") or os.urandom(32).hex()
    if environment == "production":
        logger.error(
            "SECRET_KEY/JWT_SECRET_KEY is missing in production. Generated an ephemeral key; sessions will break on restart."
        )
    else:
        logger.warning("SECRET_KEY not set; generated a temporary key for development")

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("JWT_EXPIRE_MINUTES") or os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
)
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um JWT seguro para autenticação
    """
    to_encode = data.copy()
    # JWT "sub" is expected to be a string by many libraries/validators.
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    logger.info("Token JWT criado para sub=%s, expira em %s minutos", to_encode.get("sub"), ACCESS_TOKEN_EXPIRE_MINUTES)
    return encoded_jwt
def get_current_empresa_jwt(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)) -> models.Empresa:
    """
    Dependency para rotas protegidas: extrai empresa do JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        logger.info("Decodificando JWT... (token: %s...)", token[:20] if token else "VAZIO")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info("JWT decodificado com sucesso. sub=%s", payload.get("sub"))
        
        empresa_id_raw = payload.get("sub")
        try:
            empresa_id = int(empresa_id_raw) if empresa_id_raw is not None else None
        except (TypeError, ValueError):
            empresa_id = None
        
        if empresa_id is None:
            logger.warning("JWT válido mas sem 'sub'. Payload: %s", payload)
            raise credentials_exception
            
        logger.info("Buscando empresa com ID: %s", empresa_id)
    except JWTError as e:
        logger.error("Erro ao decodificar JWT: %s", str(e))
        raise credentials_exception
    
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if empresa is None:
        logger.error("Empresa com ID %s não encontrada no banco de dados", empresa_id)
        raise credentials_exception
    
    logger.info("Autenticação bem-sucedida para empresa: %s (ID: %s)", empresa.nome_empresa, empresa.id)
    return empresa
def decode_access_token(token: str):
    """
    Decodifica e valida um JWT, retorna payload se válido, senão None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        # Keep backward compatibility in tests/app code that expects int empresa_id.
        sub = payload.get("sub")
        if isinstance(sub, str) and sub.isdigit():
            payload["sub"] = int(sub)
        return payload
    except JWTError:
        return None


# ====== Criptografia de Senhas ======
from passlib.context import CryptContext
import secrets

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração de tokens (simplificado para V1)
# NOTE: SECRET_KEY/ALGORITHM/EXPIRATIONS read from env at module top


def get_password_hash(password: str) -> str:
    """
    Cria hash seguro da senha usando bcrypt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica se a senha corresponde ao hash
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token() -> str:
    """
    Cria um token de sessão único
    """
    return secrets.token_urlsafe(32)


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_refresh_token(db: Session, empresa_id: int) -> str:
    """Create a refresh token, store hashed in DB and return token string containing jti."""
    raw = secrets.token_urlsafe(48)
    jti = uuid.uuid4().hex
    token_value = f"{jti}::{raw}"
    token_hash = _hash_token(raw)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    rt = models.RefreshToken(
        empresa_id=empresa_id,
        token_hash=token_hash,
        jti=jti,
        expires_at=expires_at,
        revoked=0
    )
    db.add(rt)
    db.commit()
    return token_value


def rotate_refresh_token(db: Session, old_jti: str, new_token_plain: str) -> Tuple[bool, Optional[str]]:
    """Mark old token revoked and create a new refresh token. Returns new token string."""
    old = db.query(models.RefreshToken).filter(models.RefreshToken.jti == old_jti, models.RefreshToken.revoked == 0).first()
    if not old:
        return False, None
    # revoke old
    old.revoked = 1
    # create new
    new_jti = uuid.uuid4().hex
    raw = new_token_plain
    token_hash = _hash_token(raw)
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    new_rt = models.RefreshToken(
        empresa_id=old.empresa_id,
        token_hash=token_hash,
        jti=new_jti,
        expires_at=expires_at,
        revoked=0,
        replaced_by=None
    )
    old.replaced_by = new_jti
    db.add(new_rt)
    db.commit()
    return True, f"{new_jti}::{raw}"


def verify_refresh_token(db: Session, token: str) -> Optional[models.RefreshToken]:
    """Verify refresh token supplied in format '<jti>::<raw>' and return DB model if valid."""
    try:
        jti, raw = token.split("::", 1)
    except Exception:
        return None
    rt = db.query(models.RefreshToken).filter(models.RefreshToken.jti == jti).first()
    if not rt or rt.revoked:
        return None
    if rt.expires_at:
        now = datetime.now(timezone.utc)
        expires_at = rt.expires_at
        # SQLite tests may return naive datetimes; normalize before comparison.
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            return None
    if _hash_token(raw) != rt.token_hash:
        return None
    return rt


def revoke_refresh_tokens_for_empresa(db: Session, empresa_id: int):
    db.query(models.RefreshToken).filter(models.RefreshToken.empresa_id == empresa_id, models.RefreshToken.revoked == 0).update({models.RefreshToken.revoked: 1})
    db.commit()
