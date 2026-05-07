"""Add avatar field

Revision ID: 005_add_avatar
Revises: 004_email_auth
Create Date: 2024-03-22
"""
from alembic import op
import sqlalchemy as sa

revision = '005_add_avatar'
down_revision = '004_email_auth'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))

def downgrade():
    op.drop_column('users', 'avatar_url') 