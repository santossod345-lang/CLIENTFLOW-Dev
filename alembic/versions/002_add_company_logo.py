"""add logo_url column to empresas table

Revision ID: 002_add_company_logo
Revises: 001_add_refresh_tokens
Create Date: 2026-02-18 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_add_company_logo'
down_revision = '001_add_refresh_tokens'
branch_labels = None
depends_on = None


def upgrade():
    # Add logo_url column to empresas table
    op.add_column('empresas', sa.Column('logo_url', sa.String(), nullable=True))


def downgrade():
    # Remove logo_url column from empresas table
    op.drop_column('empresas', 'logo_url')
