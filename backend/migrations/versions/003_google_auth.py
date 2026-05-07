"""Add Google authentication

Revision ID: 003_google_auth
Revises: 002_roles_refs
Create Date: 2024-02-17
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003_google_auth'
down_revision = '002_roles_refs'
branch_labels = None
depends_on = None

def upgrade():
    # Create google_users table
    op.create_table(
        'google_users',
        sa.Column('auth_id', sa.UUID(), sa.ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('google_id', sa.String(), unique=True, nullable=False),
        sa.Column('email', sa.String(), unique=True, nullable=False)
    )

def downgrade():
    op.drop_table('google_users') 