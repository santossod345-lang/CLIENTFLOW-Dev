"""
Middleware for ClientFlow - Request/response processing and error handling
"""

import time
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from backend.exceptions import ClientFlowException
from backend.responses import error_response
from backend.utils.logger import log_request, log_error


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware
    Catches all exceptions and returns standardized error responses
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Log request
            duration_ms = (time.time() - start_time) * 1000
            log_request(request.method, request.url.path, response.status_code, duration_ms)
            
            return response
            
        except ClientFlowException as e:
            # Handle our custom exceptions
            duration_ms = (time.time() - start_time) * 1000
            log_request(request.method, request.url.path, e.status_code, duration_ms)
            
            error_data = error_response(
                code=e.code,
                message=e.message,
                field=e.details.get("field"),
                details=e.details,
            )
            return JSONResponse(status_code=e.status_code, content=error_data)
            
        except Exception as e:
            # Handle unexpected exceptions
            duration_ms = (time.time() - start_time) * 1000
            log_request(request.method, request.url.path, 500, duration_ms)
            
            # Log the error with full context
            log_error(
                e,
                context=f"{request.method} {request.url.path}",
                details={"user_agent": request.headers.get("user-agent")}
            )
            
            error_data = error_response(
                code="INTERNAL_ERROR",
                message="Erro interno do servidor",
                details={"original_error": str(e)} if request.app.debug else None,
            )
            return JSONResponse(status_code=500, content=error_data)


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and add request context (tenant, user, etc)"""
    
    async def dispatch(self, request: Request, call_next):
        # Extract tenant from JWT token if present
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            # Token will be decoded in dependencies
            request.state.token = token
        
        response = await call_next(request)
        return response
