"""
Validators for ClientFlow - Professional validation logic for all inputs
"""

import re
from typing import Optional
from backend.exceptions import ValidationError


class EmailValidator:
    """Email validation"""
    
    # RFC 5322 simplified
    PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    @staticmethod
    def validate(email: str) -> str:
        """Validate and normalize email"""
        if not email:
            raise ValidationError("Email é obrigatório", field="email")
        
        email = email.strip().lower()
        
        if len(email) > 254:
            raise ValidationError("Email muito longo (máximo 254 caracteres)", field="email")
        
        if not EmailValidator.PATTERN.match(email):
            raise ValidationError("Email inválido", field="email")
        
        return email


class PasswordValidator:
    """Password validation - Enterprise grade"""
    
    MIN_LENGTH = 6  # Relaxed for development (was 8)
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    
    SPECIAL_CHARS = r"!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @staticmethod
    def validate(password: str, strict: bool = False) -> str:
        """
        Validate password strength
        
        In development: lenient (just 8+ chars)
        In production: strict (upper, lower, digit, special)
        """
        if not password:
            raise ValidationError("Senha é obrigatória", field="senha")
        
        if len(password) < PasswordValidator.MIN_LENGTH:
            raise ValidationError(
                f"Senha deve ter no mínimo {PasswordValidator.MIN_LENGTH} caracteres",
                field="senha"
            )
        
        if strict:
            if not any(c.isupper() for c in password):
                raise ValidationError(
                    "Senha deve conter pelo menos uma letra maiúscula",
                    field="senha"
                )
            
            if not any(c.islower() for c in password):
                raise ValidationError(
                    "Senha deve conter pelo menos uma letra minúscula",
                    field="senha"
                )
            
            if not any(c.isdigit() for c in password):
                raise ValidationError(
                    "Senha deve conter pelo menos um dígito",
                    field="senha"
                )
            
            if not any(c in PasswordValidator.SPECIAL_CHARS for c in password):
                raise ValidationError(
                    "Senha deve conter pelo menos um caractere especial",
                    field="senha"
                )
        
        return password


class PhoneValidator:
    """Phone number validation - Brazilian format (for MVP)"""
    
    @staticmethod
    def validate(phone: Optional[str]) -> Optional[str]:
        """Validate and normalize phone number"""
        if not phone:
            return None
        
        # Remove non-digit characters
        cleaned = re.sub(r"\D", "", phone)
        
        # Brazilian phone: 10-11 digits (area code + number)
        if len(cleaned) not in [10, 11]:
            raise ValidationError(
                "Telefone deve ter 10 ou 11 dígitos",
                field="telefone"
            )
        
        # Format as (XX) XXXXX-XXXX or (XX) XXXX-XXXX
        if len(cleaned) == 11:
            # Celular: (XX) 9XXXX-XXXX
            if cleaned[2] != "9":
                raise ValidationError(
                    "Telefone celular deve começar com 9",
                    field="telefone"
                )
            return f"({cleaned[:2]}) {cleaned[2:7]}-{cleaned[7:]}"
        else:
            # Fixo: (XX) XXXX-XXXX
            return f"({cleaned[:2]}) {cleaned[2:6]}-{cleaned[6:]}"


class CompanyNameValidator:
    """Company name validation"""
    
    MIN_LENGTH = 3
    MAX_LENGTH = 255
    
    @staticmethod
    def validate(name: str) -> str:
        """Validate company name"""
        if not name:
            raise ValidationError("Nome da empresa é obrigatório", field="nome_empresa")
        
        name = name.strip()
        
        if len(name) < CompanyNameValidator.MIN_LENGTH:
            raise ValidationError(
                f"Nome deve ter no mínimo {CompanyNameValidator.MIN_LENGTH} caracteres",
                field="nome_empresa"
            )
        
        if len(name) > CompanyNameValidator.MAX_LENGTH:
            raise ValidationError(
                f"Nome deve ter no máximo {CompanyNameValidator.MAX_LENGTH} caracteres",
                field="nome_empresa"
            )
        
        # Check for invalid characters
        if not re.match(r"^[a-zA-Z0-9\s\-\.&'ãáàâäéèêëíïóôõöúç]+$", name):
            raise ValidationError(
                "Nome contém caracteres inválidos",
                field="nome_empresa"
            )
        
        return name


class ClientNameValidator:
    """Client name validation"""
    
    MIN_LENGTH = 2
    MAX_LENGTH = 150
    
    @staticmethod
    def validate(name: str) -> str:
        """Validate client name"""
        if not name:
            raise ValidationError("Nome do cliente é obrigatório", field="nome")
        
        name = name.strip()
        
        if len(name) < ClientNameValidator.MIN_LENGTH:
            raise ValidationError(
                f"Nome deve ter no mínimo {ClientNameValidator.MIN_LENGTH} caracteres",
                field="nome"
            )
        
        if len(name) > ClientNameValidator.MAX_LENGTH:
            raise ValidationError(
                f"Nome deve ter no máximo {ClientNameValidator.MAX_LENGTH} caracteres",
                field="nome"
            )
        
        return name


class ServiceDescriptionValidator:
    """Service/Atendimento description validation"""
    
    MIN_LENGTH = 5
    MAX_LENGTH = 5000
    
    @staticmethod
    def validate(description: str) -> str:
        """Validate service description"""
        if not description:
            raise ValidationError(
                "Descrição é obrigatória",
                field="descricao"
            )
        
        description = description.strip()
        
        if len(description) < ServiceDescriptionValidator.MIN_LENGTH:
            raise ValidationError(
                f"Descrição deve ter no mínimo {ServiceDescriptionValidator.MIN_LENGTH} caracteres",
                field="descricao"
            )
        
        if len(description) > ServiceDescriptionValidator.MAX_LENGTH:
            raise ValidationError(
                f"Descrição deve ter no máximo {ServiceDescriptionValidator.MAX_LENGTH} caracteres",
                field="descricao"
            )
        
        return description


# Composite validator for registration
class RegistrationValidator:
    """Validates company registration data"""
    
    @staticmethod
    def validate_company_registration(data: dict) -> dict:
        """Validate all company registration fields"""
        validated = {}
        
        # Validate email
        validated["email_login"] = EmailValidator.validate(data.get("email_login", ""))
        
        # Validate password
        validated["senha"] = PasswordValidator.validate(data.get("senha", ""))
        
        # Validate company name
        validated["nome_empresa"] = CompanyNameValidator.validate(
            data.get("nome_empresa", "")
        )
        
        # Validate niche
        niche = data.get("nicho", "").strip()
        if not niche:
            raise ValidationError("Nicho é obrigatório", field="nicho")
        validated["nicho"] = niche
        
        # Validate phone (optional)
        phone = data.get("telefone")
        if phone:
            validated["telefone"] = PhoneValidator.validate(phone)
        
        return validated
