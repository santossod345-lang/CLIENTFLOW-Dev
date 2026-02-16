import os
import sqlite3
import psycopg2
from psycopg2.extras import execute_values

# Configs de origem/destino
SQLITE_DB = os.getenv("SQLITE_DB", "./clientflow.db")
PG_HOST = os.getenv("POSTGRES_HOST", "localhost")
PG_PORT = os.getenv("POSTGRES_PORT", "5432")
PG_DB = os.getenv("POSTGRES_DB", "clientflow")
PG_USER = os.getenv("POSTGRES_USER", "clientflow")
PG_PASS = os.getenv("POSTGRES_PASSWORD", "clientflow")

# Conectar SQLite
sqlite_conn = sqlite3.connect(SQLITE_DB)
sqlite_cur = sqlite_conn.cursor()

# Conectar PostgreSQL
pg_conn = psycopg2.connect(
    host=PG_HOST, port=PG_PORT, dbname=PG_DB, user=PG_USER, password=PG_PASS
)
pg_cur = pg_conn.cursor()

# Migrar empresas (schema público)
sqlite_cur.execute("SELECT * FROM empresas")
empresas = sqlite_cur.fetchall()
for emp in empresas:
    # Adapte os campos conforme necessário
    pg_cur.execute("INSERT INTO public.empresas (id, nome_empresa, nicho, telefone, email_login, senha_hash, data_cadastro, plano_empresa, data_inicio_plano, ativo, limite_clientes, limite_atendimentos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING", emp)

# Migrar clientes e atendimentos para cada empresa
for emp in empresas:
    empresa_id = emp[0]
    schema = f"empresa_{empresa_id}"
    # Clientes
    sqlite_cur.execute("SELECT * FROM clientes WHERE empresa_id=?", (empresa_id,))
    clientes = sqlite_cur.fetchall()
    for cli in clientes:
        pg_cur.execute(f"INSERT INTO {schema}.clientes VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING", cli)
    # Atendimentos
    sqlite_cur.execute("SELECT * FROM atendimentos WHERE empresa_id=?", (empresa_id,))
    atendimentos = sqlite_cur.fetchall()
    for at in atendimentos:
        pg_cur.execute(f"INSERT INTO {schema}.atendimentos VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING", at)

pg_conn.commit()
pg_cur.close()
pg_conn.close()
sqlite_cur.close()
sqlite_conn.close()
print("Migração concluída!")
