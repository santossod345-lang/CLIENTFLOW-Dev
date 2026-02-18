"""
Tenant Manager - Gerenciamento multi-tenant seguro
"""

from typing import Optional
from backend import models
from sqlalchemy.orm import Session


class TenantManager:
    """Gerencia isolamento de tenant e validações de acesso"""
    
    @staticmethod
    def verify_tenant_access(
        user_empresa_id: int,
        requested_empresa_id: int
    ) -> bool:
        """
        Verifica se usuário tem acesso ao tenant solicitado
        
        Args:
            user_empresa_id: ID da empresa do usuário
            requested_empresa_id: ID da empresa solicitada
            
        Returns:
            True se acesso permitido, False caso contrário
        """
        return user_empresa_id == requested_empresa_id
    
    @staticmethod
    def get_tenant_from_request(
        authorization_header: Optional[str],
        db: Session
    ) -> Optional[models.Empresa]:
        """Extrai tenant do JWT token"""
        from backend.auth import jwt, SECRET_KEY, ALGORITHM, JWTError
        
        if not authorization_header or not authorization_header.startswith("Bearer "):
            return None
        
        try:
            token = authorization_header.split()[1]
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            empresa_id = payload.get("sub")
            if empresa_id:
                return db.query(models.Empresa).filter(
                    models.Empresa.id == empresa_id
                ).first()
        except (JWTError, IndexError):
            return None
        
        return None
