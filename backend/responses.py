"""
Standardized API response types - Consistent API responses across all endpoints
Inspired by Stripe, GitHub, and enterprise APIs
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


T = TypeVar("T")


class StatusEnum(str, Enum):
    """API Response Status"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


class PaginationInfo(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., ge=1, description="Page number (1-indexed)")
    page_size: int = Field(..., ge=1, le=100, description="Items per page")
    total_items: int = Field(..., ge=0, description="Total items in database")
    total_pages: int = Field(..., ge=0, description="Total pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")
    
    class Config:
        json_schema_extra = {
            "example": {
                "page": 1,
                "page_size": 20,
                "total_items": 150,
                "total_pages": 8,
                "has_next": True,
                "has_prev": False
            }
        }


class ErrorDetail(BaseModel):
    """Error detail - specific error information"""
    code: str = Field(..., description="Error code (machine-readable)")
    message: str = Field(..., description="Error message (human-readable)")
    field: Optional[str] = Field(None, description="Field that caused error (validation only)")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error context")
    
    class Config:
        json_schema_extra = {
            "example": {
                "code": "VALIDATION_ERROR",
                "message": "Email already exists",
                "field": "email_login",
                "details": {"resource": "Empresa"}
            }
        }


class SuccessResponse(BaseModel, Generic[T]):
    """
    Standard success response - Used for all successful API calls
    
    Example:
    {
        "status": "success",
        "data": {...},
        "message": "Empresa criada com sucesso",
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    status: StatusEnum = Field(default=StatusEnum.SUCCESS, description="Response status")
    data: Optional[T] = Field(None, description="Response payload")
    message: Optional[str] = Field(None, description="Success message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated success response - For list endpoints
    
    Example:
    {
        "status": "success",
        "data": [...],
        "message": "10 clientes encontrados",
        "pagination": {...},
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    status: StatusEnum = Field(default=StatusEnum.SUCCESS)
    data: List[T] = Field(..., description="List of items")
    message: Optional[str] = Field(None)
    pagination: PaginationInfo = Field(..., description="Pagination metadata")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


class ErrorResponse(BaseModel):
    """
    Standard error response - Used for all API errors
    
    Example:
    {
        "status": "error",
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Email already exists",
            "field": "email_login"
        },
        "timestamp": "2024-01-15T10:30:00Z"
    }
    """
    status: StatusEnum = Field(default=StatusEnum.ERROR)
    error: ErrorDetail = Field(..., description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }


# Helper functions to create responses

def success_response(
    data: Optional[Any] = None,
    message: Optional[str] = None,
    status: StatusEnum = StatusEnum.SUCCESS,
) -> Dict[str, Any]:
    """Create a success response"""
    return {
        "status": status,
        "data": data,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def paginated_response(
    data: List[Any],
    page: int,
    page_size: int,
    total_items: int,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a paginated response"""
    total_pages = (total_items + page_size - 1) // page_size
    return {
        "status": StatusEnum.SUCCESS,
        "data": data,
        "message": message or f"{len(data)} itens encontrados",
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_items": total_items,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


def error_response(
    code: str,
    message: str,
    field: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create an error response"""
    return {
        "status": StatusEnum.ERROR,
        "error": {
            "code": code,
            "message": message,
            "field": field,
            "details": details,
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
