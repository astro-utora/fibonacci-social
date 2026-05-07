"""Add waiting_list table

Revision ID: 021_add_waiting_list_table
Revises: 020_add_project_id_to_fillout
Create Date: 2025-03-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import table, column, select, text
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '021_add_waiting_list_table'
down_revision = '020_add_project_id_to_fillout'
branch_labels = None
depends_on = None


def upgrade():
    # Create waiting_list table
    op.create_table(
        'waiting_list',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default="pending"),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='CASCADE'),
    )
    
    # Create an index on user_id for faster lookups
    op.create_index('idx_waiting_list_user_id', 'waiting_list', ['user_id'])
    
    # Create an index on status for filtering
    op.create_index('idx_waiting_list_status', 'waiting_list', ['status'])
    
    # Add all existing users to the waiting list with 'approved' status
    connection = op.get_bind()
    
    # Get all existing user UUIDs
    users = connection.execute(text("SELECT uuid FROM users")).fetchall()
    
    # Current timestamp for approved_at
    now = datetime.utcnow()
    
    # Insert entries for all existing users with 'approved' status
    for user in users:
        connection.execute(
            text("""
                INSERT INTO waiting_list (user_id, status, approved_at, created_at) 
                VALUES (:user_id, 'approved', :approved_at, :created_at)
            """),
            {"user_id": user[0], "approved_at": now, "created_at": now}
        )


def downgrade():
    # Drop the waiting_list table and all associated indexes and constraints
    op.drop_table('waiting_list') 