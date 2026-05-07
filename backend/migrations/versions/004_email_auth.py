"""Add email authentication

Revision ID: 004_email_auth
Revises: 003_google_auth
Create Date: 2024-03-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '004_email_auth'
down_revision = '003_google_auth'
branch_labels = None
depends_on = None

def upgrade():
    # Add email to auth_provider enum
    op.execute("ALTER TYPE auth_provider ADD VALUE 'email'")
    
    # Create email_users table
    op.create_table(
        'email_users',
        sa.Column('auth_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), server_default='false'),
        sa.Column('verification_token', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['auth_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('auth_id'),
        sa.UniqueConstraint('email')
    )

def downgrade():
    op.drop_table('email_users') 