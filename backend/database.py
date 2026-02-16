import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

# Configuração via variáveis de ambiente
POSTGRES_USER = os.getenv("POSTGRES_USER", "clientflow")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "clientflow")
POSTGRES_DB = os.getenv("POSTGRES_DB", "clientflow")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

# Engine PostgreSQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
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
