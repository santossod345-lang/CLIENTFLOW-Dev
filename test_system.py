#!/usr/bin/env python
"""
Script de teste rápido para validar a integridade do sistema
"""
import sys

def test_imports():
    """Testar se todos os imports funcionam"""
    try:
        print("➤ Testando imports...")
        from backend import models, database, auth
        from backend.routers import empresa, clientes, dashboard
        from backend.dependencies import require_authenticated_empresa
        from backend.schemas import EmpresaOut, ClienteOut
        print("✓ Todos os imports OK")
        return True
    except Exception as e:
        print(f"✗ Erro no import: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_config():
    """Testar configuração do banco de dados"""
    try:
        print("\n➤ Testando configuração do banco de dados...")
        from backend import database
        print(f"✓ Database URL: {database.SQLALCHEMY_DATABASE_URL[:50]}...")
        return True
    except Exception as e:
        print(f"✗ Erro na database: {e}")
        return False


def test_models():
    """Testar se os modelos podem ser criados"""
    try:
        print("\n➤ Testando modelos...")
        from backend import models
        # Verificar se os atributos dos modelos existem
        assert hasattr(models.Empresa, '__tablename__')
        assert hasattr(models.Cliente, '__tablename__')
        assert hasattr(models.Atendimento, '__tablename__')
        print("✓ Modelos OK")
        return True
    except Exception as e:
        print(f"✗ Erro nos modelos: {e}")
        return False


def test_auth_functions():
    """Testar se as funções de auth existem"""
    try:
        print("\n➤ Testando funções de autenticação...")
        from backend import auth
        assert callable(auth.create_access_token)
        assert callable(auth.get_password_hash)
        assert callable(auth.verify_password)
        print("✓ Funções de autenticação OK")
        return True
    except Exception as e:
        print(f"✗ Erro nas funções de auth: {e}")
        return False


def test_schemas():
    """Testar se os schemas Pydantic estão corretos"""
    try:
        print("\n➤ Testando schemas...")
        from backend.schemas import EmpresaOut, ClienteOut, TokenResponse
        
        # Teste de modelo Pydantic
        empresa_data = {
            "id": 1,
            "nome_empresa": "Test Co",
            "nicho": "Tech",
            "email_login": "test@example.com",
            "telefone": "1234567890"
        }
        empresa = EmpresaOut(**empresa_data)
        print("✓ Schemas OK")
        return True
    except Exception as e:
        print(f"✗ Erro nos schemas: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_routers():
    """Testar se os routers têm as rotas""" 
    try:
        print("\n➤ Testando routers...")
        from backend.routers import empresa, clientes, dashboard
        assert hasattr(empresa, 'router')
        assert hasattr(clientes, 'router')
        assert hasattr(dashboard, 'router')
        print("✓ Routers OK")
        return True
    except Exception as e:
        print(f"✗ Erro nos routers: {e}")
        return False


def main():
    print("=" * 60)
    print("TESTE DE INTEGRIDADE DO CLIENTFLOW")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_database_config,
        test_models,
        test_auth_functions,
        test_schemas,
        test_routers,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"✗ Erro inesperado em {test.__name__}: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTADO: {passed}/{total} testes passaram")
    
    if passed == total:
        print("✓ SISTEMA FUNCIONANDO CORRETAMENTE!")
        print("=" * 60)
        return 0
    else:
        print("✗ SISTEMA COM PROBLEMAS - Revisar erros acima")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
