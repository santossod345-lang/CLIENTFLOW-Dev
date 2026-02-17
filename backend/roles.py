from fastapi import Depends
from backend import models
from typing import List


def require_roles(_required: List[str] = None):
    def _checker(empresa: models.Empresa = Depends(lambda: None)):
        # Placeholder: integrate with Empresa.roles or user model when available
        # For now, allow by default; implement real checks when RBAC model exists
        return True
    return _checker
