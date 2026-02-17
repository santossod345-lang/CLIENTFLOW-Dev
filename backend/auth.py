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
# OAuth2 scheme para extrair o token do header Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/empresas/login")
SECRET_KEY = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY") or ""
if not SECRET_KEY:
    # Fallback to a runtime-generated key (not for production)
    SECRET_KEY = os.getenv("SECRET_KEY_RUNTIME", "") or os.urandom(32).hex()

ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um JWT seguro para autenticação
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        empresa_id: int = payload.get("sub")
        if empresa_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if empresa is None:
        raise credentials_exception
    return empresa
def decode_access_token(token: str):
    """
    Decodifica e valida um JWT, retorna payload se válido, senão None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    if rt.expires_at and rt.expires_at < datetime.now(timezone.utc):
        return None
    if _hash_token(raw) != rt.token_hash:
        return None
    return rt


def revoke_refresh_tokens_for_empresa(db: Session, empresa_id: int):
    db.query(models.RefreshToken).filter(models.RefreshToken.empresa_id == empresa_id, models.RefreshToken.revoked == 0).update({models.RefreshToken.revoked: 1})
    db.commit()
