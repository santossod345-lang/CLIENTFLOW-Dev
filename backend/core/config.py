"""
Configuration settings for ClientFlow - Billion-dollar SaaS platform
"""

import os
from functools import lru_cache
from typing import Optional


class Settings:
    """Application settings - centralized configuration"""
    
    # App metadata
    APP_NAME: str = "ClientFlow"
    APP_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-NOW!")
    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
    
    # Database
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # CORS
    CORS_ORIGINS: list = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:8000").split(",")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    
    # Features
    ENABLE_AI_ASSISTANT: bool = os.getenv("ENABLE_AI_ASSISTANT", "false").lower() == "true"
    
    # Tenant configuration
    MAX_COMPANIES_PER_USER: int = 10
    MAX_CLIENTS_PER_COMPANY: int = int(os.getenv("MAX_CLIENTS_PER_COMPANY", "10000"))
    MAX_SERVICES_PER_COMPANY: int = int(os.getenv("MAX_SERVICES_PER_COMPANY", "50000"))
    
    def __init__(self):
        """Validate critical settings on initialization"""
        if self.SECRET_KEY == "your-secret-key-change-in-production-NOW!":
            if self.ENVIRONMENT == "production":
                raise ValueError("SECRET_KEY must be set in production!")
    
    class Config:
        """Pydantic config"""
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()
