import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configuração via variáveis de ambiente
# Prioriza DATABASE_URL (Railway/Heroku), senão usa SQLite local
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Railway/Heroku fornecem DATABASE_URL
    # Substitui postgres:// por postgresql+psycopg2:// se necessário
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    # Fallback para SQLite local (desenvolvimento)
    SQLALCHEMY_DATABASE_URL = "sqlite:///./clientflow.db"

# Engine - SQLite ou PostgreSQL
# Para SQLite: sem pool pré-ping (SQLite em arquivo é simples)
# Para PostgreSQL: com pool_pre_ping para health check
if "sqlite" in SQLALCHEMY_DATABASE_URL:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )
else:
    # PostgreSQL
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20,
        echo=False,
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
