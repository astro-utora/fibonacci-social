"""Add credits table

Revision ID: 018_add_credits_table
Revises: 017_add_projects_tables
Create Date: 2025-03-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '018_add_credits_table'
down_revision = '017_add_projects_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create credits table
    op.create_table(
        'credits',
        sa.Column('id', UUID(), primary_key=True, nullable=False),
        sa.Column('user_uuid', UUID(), nullable=False),
        sa.Column('credits', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=text('now()'), onupdate=text('now()')),
        sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], name='fk_credits_user_uuid', ondelete='CASCADE'),
    )
    
    # Add index for faster user lookup
    op.create_index('ix_credits_user_uuid', 'credits', ['user_uuid'])


def downgrade() -> None:
    # Remove indexes and foreign keys
    op.drop_index('ix_credits_user_uuid', 'credits')
    
    # Drop credits table
    op.drop_table('credits') 