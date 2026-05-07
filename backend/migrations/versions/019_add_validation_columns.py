"""Add validation columns to fillout submissions

Revision ID: 019_add_validation_columns
Revises: 018_add_credits_table
Create Date: 2025-03-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '019_add_validation_columns'
down_revision = '018_add_credits_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add requested_at and validated_at columns to fillout_submissions table
    op.add_column('fillout_submissions', sa.Column('requested_at', sa.DateTime(), nullable=True))
    op.add_column('fillout_submissions', sa.Column('validated_at', sa.DateTime(), nullable=True))
    
    # Update status function in API responses
    # Note: This is handled in application code, not in the database


def downgrade() -> None:
    # Remove the columns
    op.drop_column('fillout_submissions', 'validated_at')
    op.drop_column('fillout_submissions', 'requested_at') 