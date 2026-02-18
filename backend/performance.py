"""
Performance Module - Caching, índices, otimizações
FASE 4: Performance & Optimization
"""

from functools import lru_cache
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import json

from backend.utils import get_logger

logger = get_logger("clientflow.performance")


class CacheManager:
    """
    Simple in-memory cache com TTL
    Em produção, usar Redis
    """
    
    def __init__(self):
        self._cache: Dict[str, tuple] = {}  # key -> (value, ttl_timestamp)
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        if key not in self._cache:
            return None
        
        value, ttl = self._cache[key]
        
        # Verifica se expirou
        if datetime.now() > ttl:
            del self._cache[key]
            return None
        
        logger.debug(f"Cache hit: {key}")
        return value
    
    def set(self, key: str, value: Any, ttl_seconds: int = 300):
        """Define valor no cache com TTL"""
        ttl = datetime.now() + timedelta(seconds=ttl_seconds)
        self._cache[key] = (value, ttl)
        logger.debug(f"Cache set: {key} (TTL: {ttl_seconds}s)")
    
    def delete(self, key: str):
        """Remove valor do cache"""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache deleted: {key}")
    
    def clear(self):
        """Limpa todo o cache"""
        self._cache.clear()
        logger.info("Cache cleared")


# Instância global
cache = CacheManager()


@lru_cache(maxsize=128)
def expensive_calculation(value: str) -> str:
    """
    Cacheia cálculo custoso usando LRU
    """
    logger.debug(f"Computing expensive calculation for: {value}")
    # Simulando cálculo custoso
    return f"calculated_{value}"


class DatabaseIndexHints:
    """
    Dicas de índices para otimizar queries
    Em produção, executar:
    
    CREATE INDEX idx_empresa_email ON empresas(email_login);
    CREATE INDEX idx_cliente_empresa ON clientes(empresa_id);
    CREATE INDEX idx_atendimento_empresa ON atendimentos(empresa_id);
    CREATE INDEX idx_atendimento_data ON atendimentos(data_atendimento);
    CREATE INDEX idx_cliente_empresa_telefone ON clientes(empresa_id, telefone);
    CREATE INDEX idx_atendimento_cliente ON atendimentos(cliente_id);
    """
    
    INDEXES = {
        "empresas": [
            "email_login",  # Para login rápido
            ("email_login", "ativo"),  # Para filtros
        ],
        "clientes": [
            "empresa_id",  # Para listar clientes
            ("empresa_id", "telefone"),  # Para buscar por telefone
            "data_primeiro_contato",  # Para ordenação
        ],
        "atendimentos": [
            "empresa_id",  # Para listar atendimentos
            "cliente_id",  # Para relacionamento
            "data_atendimento",  # Para ordenação temporal
            ("empresa_id", "data_atendimento"),  # Combo para analytics
        ],
    }


class PaginationOptimizer:
    """
    Otimização de paginação
    """
    
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    @staticmethod
    def validate_pagination(skip: int, limit: int) -> tuple[int, int]:
        """
        Valida e normaliza parâmetros de paginação
        
        Returns: (skip, limit)
        """
        # Garantir valores positivos
        skip = max(0, skip)
        limit = max(1, limit)
        
        # Limitar máximo
        limit = min(limit, PaginationOptimizer.MAX_PAGE_SIZE)
        
        logger.debug(f"Pagination: skip={skip}, limit={limit}")
        return skip, limit
    
    @staticmethod
    def get_page_info(skip: int, limit: int, total: int) -> dict:
        """Calcula informações de paginação"""
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return {
            "page": page,
            "page_size": limit,
            "total_items": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1,
        }


class QueryOptimizer:
    """
    Dicas de otimização de queries SQLAlchemy
    """
    
    @staticmethod
    def tips():
        """
        Best practices para queries SQLAlchemy:
        
        1. Use eager loading para relacionamentos:
           query.options(joinedload(Empresa.clientes))
        
        2. Use select com índices:
           query.where(Empresa.email_login == email)
        
        3. Pagine resultados:
           query.offset(skip).limit(limit)
        
        4. Use contains_eager para filtered loads:
           query.options(contains_eager(Empresa.clientes))
        
        5. Evite N+1 queries com bulk operations
        """
        pass


class PerformanceMonitor:
    """
    Monitor simples de performance
    """
    
    def __init__(self):
        self._metrics: Dict[str, list] = {}
    
    def record_time(self, operation: str, duration_ms: float):
        """Registra tempo de operação"""
        if operation not in self._metrics:
            self._metrics[operation] = []
        
        self._metrics[operation].append(duration_ms)
        
        # Manter últimos 100 records
        if len(self._metrics[operation]) > 100:
            self._metrics[operation].pop(0)
    
    def get_stats(self, operation: str) -> Dict[str, float]:
        """Obtém estatísticas de operação"""
        if operation not in self._metrics or not self._metrics[operation]:
            return {}
        
        times = self._metrics[operation]
        return {
            "count": len(times),
            "min_ms": min(times),
            "max_ms": max(times),
            "avg_ms": sum(times) / len(times),
        }


# Instância global
monitor = PerformanceMonitor()
