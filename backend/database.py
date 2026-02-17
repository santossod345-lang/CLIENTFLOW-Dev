import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configuração via variáveis de ambiente
# Prioriza DATABASE_URL (Railway/Heroku), senão usa variáveis individuais
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Railway/Heroku fornecem DATABASE_URL
    # Substitui postgres:// por postgresql+psycopg2:// se necessário
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Fallback para variáveis individuais (desenvolvimento local)
    POSTGRES_USER = os.getenv("POSTGRES_USER", "clientflow")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "clientflow")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "clientflow")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    SQLALCHEMY_DATABASE_URL = (
        f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )

# Engine PostgreSQL
# Nota: pool_pre_ping faz health check antes de usar conexões do pool
# Não falha no import - apenas quando tentar usar a conexão
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False,  # Set to True for SQL query logging
)

# Session factory (scoped para threads)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

# Base para os modelos
Base = declarative_base()

# Função para criar schema por empresa (multi-tenant)
def create_tenant_schema(schema_name: str):
    with engine.connect() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))

# Dependência para obter sessão do banco de dados
def get_db(schema: str = None):
    db = SessionLocal()
    if schema:
        db.execute(text(f"SET search_path TO {schema}, public"))
    try:
        yield db
    finally:
        db.close()
