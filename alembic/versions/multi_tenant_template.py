"""
Script de migração multi-schema para todos os tenants (empresas)
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Exemplo: rodar upgrade em todos os schemas de empresas
    bind = op.get_bind()
    schemas = [r[0] for r in bind.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'empresa_%'")]
    for schema in schemas:
        op.create_table(
            'clientes',
            sa.Column('id', sa.Integer, primary_key=True),
            # ...demais colunas...
            schema=schema
        )
        # Repita para outras tabelas

def downgrade():
    bind = op.get_bind()
    schemas = [r[0] for r in bind.execute("SELECT schema_name FROM information_schema.schemata WHERE schema_name LIKE 'empresa_%'")]
    for schema in schemas:
        op.drop_table('clientes', schema=schema)
        # Repita para outras tabelas
