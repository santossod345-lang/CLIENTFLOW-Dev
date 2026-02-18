"""
Security Module - Rate limiting, CORS, proteção contra ataques
FASE 3: Segurança Avançada
"""

import time
from typing import Dict, Optional
from collections import defaultdict
from fastapi import Request, HTTPException, status
from backend.core.config import settings
from backend.utils import log_error, get_logger

logger = get_logger("clientflow.security")


class RateLimiter:
    """
    Rate limiter simples em memória
    Em produção, usar Redis para distribuído
    """
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, list] = defaultdict()
    
    def is_allowed(self, key: str) -> bool:
        """Verifica se requisição é permitida"""
        now = time.time()
        one_minute_ago = now - 60
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove requisições antigas
        self.requests[key] = [
            req_time for req_time in self.requests[key]
            if req_time > one_minute_ago
        ]
        
        # Verifica limite
        if len(self.requests[key]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for key: {key}")
            return False
        
        # Registra nova requisição
        self.requests[key].append(now)
        return True


# Instância global
rate_limiter = RateLimiter(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)


def get_client_ip(request: Request) -> str:
    """
    Extrai IP do cliente considerando proxies
    """
    # X-Forwarded-For vem em ordem de proxies (mais recente à direita)
    if "x-forwarded-for" in request.headers:
        return request.headers["x-forwarded-for"].split(",")[0].strip()
    
    # Fallback para conexão direta
    return request.client.host if request.client else "unknown"


async def rate_limit_check(request: Request) -> bool:
    """Middleware para verificar rate limit"""
    if not settings.RATE_LIMIT_ENABLED:
        return True
    
    client_ip = get_client_ip(request)
    
    # Endpoints isentos de rate limit
    exempt_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
    if any(request.url.path.startswith(path) for path in exempt_paths):
        return True
    
    if not rate_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}, Path: {request.url.path}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Muitas requisições. Tente novamente mais tarde."
        )
    
    return True


def validate_user_agent(user_agent: Optional[str]) -> bool:
    """
    Valida user agent contra bots conhecidos
    Retorna True se é um cliente legítimo
    """
    if not user_agent:
        return True  # Allow missing user agents
    
    user_agent_lower = user_agent.lower()
    
    # Bloqueir user agents suspeitos
    suspicious_patterns = [
        "bad-bot",
        "malicious-bot",
        "crawler",
        "scraper",
    ]
    
    for pattern in suspicious_patterns:
        if pattern in user_agent_lower:
            logger.warning(f"Suspicious user agent blocked: {user_agent}")
            return False
    
    return True


def check_cors_origin(origin: str, allowed_origins: list) -> bool:
    """Verifica CORS origin"""
    if "*" in allowed_origins:
        return True
    
    return origin in allowed_origins


class SecurityHeaders:
    """Headers de segurança profissionais"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """Retorna headers de segurança recomendados"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }


class InputValidator:
    """Validação de entrada contra ataques comuns"""
    
    DANGEROUS_PATTERNS = [
        r"<script",
        r"javascript:",
        r"on\w+\s*=",  # onclick, onload, etc
        r"--",  # SQL comment
        r"\'.*or.*\'",  # SQL injection
        r";\s*drop",  # SQL injection
    ]
    
    @staticmethod
    def is_safe(value: str) -> bool:
        """Verifica se valor é seguro"""
        if not isinstance(value, str):
            return True
        
        import re
        for pattern in InputValidator.DANGEROUS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"Dangerous input detected: {value[:50]}")
                return False
        
        return True
    
    @staticmethod
    def validate_input(data: dict) -> bool:
        """Valida todos os campos de um dict"""
        for key, value in data.items():
            if isinstance(value, str) and not InputValidator.is_safe(value):
                logger.warning(f"Unsafe input in field '{key}'")
                return False
        
        return True
