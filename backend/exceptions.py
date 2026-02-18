"""
Custom exceptions for ClientFlow API - Centralized error handling
"""

from typing import Any, Dict, Optional


class ClientFlowException(Exception):
    """Base exception for all ClientFlow errors"""
    
    def __init__(
        self,
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ClientFlowException):
    """Raised when data validation fails"""
    
    def __init__(self, message: str, field: Optional[str] = None, details=None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=422,
            details={"field": field, **(details or {})},
        )


class AuthenticationError(ClientFlowException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Não autenticado", details=None):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details or {},
        )


class AuthorizationError(ClientFlowException):
    """Raised when user is not authorized to perform action"""
    
    def __init__(self, message: str = "Não autorizado", details=None):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details or {},
        )


class NotFoundError(ClientFlowException):
    """Raised when resource is not found"""
    
    def __init__(
        self, resource: str = "Recurso", resource_id: Optional[Any] = None, details=None
    ):
        message = f"{resource} não encontrado"
        if resource_id:
            message = f"{resource} com ID {resource_id} não encontrado"
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details={"resource": resource, "resource_id": resource_id, **(details or {})},
        )


class ConflictError(ClientFlowException):
    """Raised when resource already exists"""
    
    def __init__(self, message: str, resource: Optional[str] = None, details=None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details={"resource": resource, **(details or {})},
        )


class TenantError(ClientFlowException):
    """Raised for multi-tenant isolation violations"""
    
    def __init__(self, message: str = "Erro de isolamento de tenant", details=None):
        super().__init__(
            message=message,
            code="TENANT_ERROR",
            status_code=403,
            details=details or {},
        )


class RateLimitError(ClientFlowException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Muitas requisições", details=None):
        super().__init__(
            message=message,
            code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details or {},
        )


class DatabaseError(ClientFlowException):
    """Raised for database operation errors"""
    
    def __init__(self, message: str = "Erro no banco de dados", details=None):
        super().__init__(
            message=message,
            code="DATABASE_ERROR",
            status_code=500,
            details=details or {},
        )


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid or expired"""
    
    def __init__(self, message: str = "Token inválido ou expirado"):
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Raised when token is expired"""
    
    def __init__(self, message: str = "Token expirado"):
        super().__init__(message)
