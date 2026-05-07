"""Add payments table and willing_to_contribute field

Revision ID: 014_add_payments_table
Revises: 013_create_fillout_submissions
Create Date: 2025-02-28
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '014_add_payments_table'
down_revision = '013_create_fillout_submissions'  # Update this to your actual previous migration
branch_labels = None
depends_on = None

def upgrade():
    # Add willing_to_contribute column to users table
    op.add_column('users', sa.Column('willing_to_contribute', sa.Boolean(), nullable=True))
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('payment_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=True),
        sa.Column('total_amount', sa.Float(), nullable=True),
        sa.Column('currency', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_payments_email'), 'payments', ['email'], unique=False)
    op.create_index(op.f('ix_payments_payment_id'), 'payments', ['payment_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_payments_payment_id'), table_name='payments')
    op.drop_index(op.f('ix_payments_email'), table_name='payments')
    op.drop_table('payments')
    op.drop_column('users', 'willing_to_contribute') 