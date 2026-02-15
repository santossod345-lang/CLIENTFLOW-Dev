"""
Sistema de autenticação e segurança
"""
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import secrets

# Configuração do contexto de criptografia
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração de tokens (simplificado para V1)
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 horas


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
