"""
Logging utilities for ClientFlow - Structured logging for debugging and monitoring
"""

import logging
import json
from datetime import datetime
from typing import Any, Dict, Optional
from backend.core.config import settings


# Configure logging format
LOGGING_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(format=LOGGING_FORMAT, level=settings.LOG_LEVEL)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)


logger = get_logger("clientflow")


def log_action(
    action: str,
    entity: str,
    entity_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    level: str = "INFO"
):
    """
    Log an action - useful for audit trail
    
    Args:
        action: Action performed (create, update, delete, etc)
        entity: Entity type (empresa, cliente, atendimento, etc)
        entity_id: ID of the entity
        usuario_id: ID of the user performing action
        details: Additional details
        level: Log level
    """
    log_data = {
        "action": action,
        "entity": entity,
        "entity_id": entity_id,
        "usuario_id": usuario_id,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    log_message = json.dumps(log_data, ensure_ascii=False, default=str)
    
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(f"ACTION: {log_message}")


def log_error(
    error: Exception,
    context: Optional[str] = None,
    user_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None
):
    """
    Log an error with context
    
    Args:
        error: The exception
        context: What was happening when error occurred
        user_id: User ID if applicable
        details: Additional context
    """
    error_data = {
        "error": str(error),
        "error_type": type(error).__name__,
        "context": context,
        "user_id": user_id,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    log_message = json.dumps(error_data, ensure_ascii=False, default=str)
    logger.error(f"ERROR: {log_message}", exc_info=True)


def log_auth(action: str, email: str, success: bool, details: Optional[Dict] = None):
    """
    Log authentication events
    
    Args:
        action: login, logout, refresh, etc
        email: User email
        success: Whether action was successful
        details: Additional details (IP, user agent, etc)
    """
    auth_data = {
        "action": action,
        "email": email,
        "success": success,
        "details": details or {},
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    log_message = json.dumps(auth_data, ensure_ascii=False, default=str)
    level = "INFO" if success else "WARNING"
    log_func = getattr(logger, level.lower())
    log_func(f"AUTH: {log_message}")


def log_request(method: str, path: str, status_code: int, duration_ms: float):
    """
    Log HTTP request
    
    Args:
        method: HTTP method
        path: Request path
        status_code: Response status code
        duration_ms: Request duration in milliseconds
    """
    request_data = {
        "method": method,
        "path": path,
        "status_code": status_code,
        "duration_ms": duration_ms,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
    
    log_message = json.dumps(request_data, ensure_ascii=False, default=str)
    
    if 200 <= status_code < 300:
        logger.info(f"REQUEST: {log_message}")
    elif 300 <= status_code < 400:
        logger.info(f"REQUEST: {log_message}")
    elif 400 <= status_code < 500:
        logger.warning(f"REQUEST: {log_message}")
    else:
        logger.error(f"REQUEST: {log_message}")
