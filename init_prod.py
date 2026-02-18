#!/usr/bin/env python
"""
Initialize script for ClientFlow production deployment
Run migrations and verify database connection before starting the app
"""

import os
import sys
import time
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('clientflow.init')

def check_database_connection(max_retries=5):
    """
    Verificar conexão com banco de dados com retry
    """
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        logger.error("DATABASE_URL não está configurada!")
        return False
    
    logger.info(f"Conectando ao banco de dados: {database_url.split('@')[0]}...")
    
    for attempt in range(max_retries):
        try:
            engine = create_engine(database_url, echo=False)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ Conexão com banco de dados OK")
            engine.dispose()
            return True
        except OperationalError as e:
            wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4, 8, 16 segundos
            logger.warning(f"Tentativa {attempt + 1}/{max_retries} falhou. Retry em {wait_time}s...")
            time.sleep(wait_time)
        except Exception as e:
            logger.error(f"Erro ao conectar no banco: {e}")
            return False
    
    logger.error("Falha ao conectar ao banco após múltiplas tentativas")
    return False

def run_migrations():
    """
    Run Alembic migrations
    """
    logger.info("Executando migrations...")
    
    try:
        os.system("python -m alembic upgrade head")
        logger.info("✓ Migrations executadas com sucesso")
        return True
    except Exception as e:
        logger.error(f"Erro ao executar migrations: {e}")
        return False

def verify_environment():
    """
    Verify all required environment variables
    """
    required_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'ENVIRONMENT',
    ]
    
    logger.info("Verificando variáveis de ambiente...")
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
            logger.warning(f"  ⚠ {var} não definida")
        else:
            logger.info(f"  ✓ {var} configurada")
    
    if missing:
        logger.error(f"Variáveis obrigatórias faltando: {', '.join(missing)}")
        return False
    
    return True

def create_upload_directories():
    """
    Create required upload directories
    """
    logger.info("Criando diretórios de upload...")
    
    try:
        os.makedirs("uploads/logos", exist_ok=True)
        logger.info("✓ Diretórios de upload criados")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar diretórios: {e}")
        return False

def main():
    """
    Main initialization routine
    """
    logger.info("=" * 60)
    logger.info("ClientFlow - Inicialização de Produção")
    logger.info("=" * 60)
    
    # Passo 1: Verificar variáveis
    if not verify_environment():
        logger.error("Falha na verificação de ambiente. Abortando.")
        sys.exit(1)
    
    # Passo 2: Criar diretórios
    if not create_upload_directories():
        logger.warning("Aviso ao criar diretórios (pode continuar)")
    
    # Passo 3: Verificar banco
    if not check_database_connection():
        logger.error("Falha na conexão com banco. Abortando.")
        sys.exit(1)
    
    # Passo 4: Executar migrations
    if not run_migrations():
        logger.error("Falha ao executar migrations. Abortando.")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("✓ Inicialização concluída com sucesso!")
    logger.info("=" * 60)
    return 0

if __name__ == "__main__":
    sys.exit(main())
