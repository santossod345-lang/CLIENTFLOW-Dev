#!/usr/bin/env python
"""
Script de teste para diagnosticar o fluxo de autenticação
"""

import os
import sys
import json

# Adicionar o diretório ao path
sys.path.insert(0, os.path.dirname(__file__))

from backend import auth, models, database
from sqlalchemy.orm import Session

def test_jwt_creation():
    """Testa a criação e verificação de JWT"""
    print("\n=== TESTE 1: Criação de JWT ===")
    
    # Criar um token
    empresa_id = 123
    token = auth.create_access_token({"sub": empresa_id})
    print(f"✓ Token criado: {token[:50]}...")
    
    # Decodificar o token
    payload = auth.decode_access_token(token)
    print(f"✓ Token decodificado: {payload}")
    
    if payload and "sub" in payload:
        print(f"✓ sub (empresa_id) extraído: {payload['sub']}")
    else:
        print("✗ ERRO: sub não encontrado no token!")
        return False
    
    return True

def test_refresh_token():
    """Testa a criação de refresh token"""
    print("\n=== TESTE 2: Refresh Token ===")
    
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Usar banco em memória para teste
    engine = create_engine("sqlite:///:memory:")
    models.Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        # Criar uma empresa
        empresa = models.Empresa(
            nome_empresa="Test Company",
            nicho="test",
            email_login="test@example.com",
            senha_hash=auth.get_password_hash("test123"),
        )
        db.add(empresa)
        db.commit()
        db.refresh(empresa)
        print(f"✓ Empresa criada com ID: {empresa.id}")
        
        # Criar refresh token
        refresh_token = auth.create_refresh_token(db, empresa.id)
        print(f"✓ Refresh token criado: {refresh_token[:50]}...")
        
        # Verificar refresh token
        rt = auth.verify_refresh_token(db, refresh_token)
        if rt and rt.empresa_id == empresa.id:
            print(f"✓ Refresh token válido para empresa {rt.empresa_id}")
            return True
        else:
            print("✗ ERRO: refresh token inválido!")
            return False
            
    finally:
        db.close()

def test_password_hash():
    """Testa hashing de senha"""
    print("\n=== TESTE 3: Password Hashing ===")
    
    senha = "test123"
    hash_senha = auth.get_password_hash(senha)
    print(f"✓ Senha hasheada: {hash_senha[:50]}...")
    
    # Verificar se a senha corresponde
    if auth.verify_password(senha, hash_senha):
        print(f"✓ Senha verificada corretamente")
        return True
    else:
        print("✗ ERRO: Senha não corresponde ao hash!")
        return False

def main():
    print("=" * 60)
    print("AUDITORIA DE AUTENTICAÇÃO - ClientFlow")
    print("=" * 60)
    
    all_passed = True
    
    try:
        all_passed &= test_jwt_creation()
    except Exception as e:
        print(f"✗ ERRO no teste de JWT: {e}")
        all_passed = False
    
    try:
        all_passed &= test_refresh_token()
    except Exception as e:
        print(f"✗ ERRO no teste de refresh token: {e}")
        all_passed = False
    
    try:
        all_passed &= test_password_hash()
    except Exception as e:
        print(f"✗ ERRO no teste de password hash: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ TODOS OS TESTES PASSARAM")
        print("Backend de autenticação está funcionando corretamente")
    else:
        print("✗ ALGUNS TESTES FALHARAM")
        print("Há problemas no sistema de autenticação")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
