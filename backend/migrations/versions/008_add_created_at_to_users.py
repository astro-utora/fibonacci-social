"""add created_at to users

Revision ID: 008_add_created_at_to_users
Revises: 007_dynamic_roles
Create Date: 2024-02-19 03:21:44.231

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '008_add_created_at_to_users'
down_revision: Union[str, None] = '007_dynamic_roles'  # Point to previous migration
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add created_at column with default value
    op.add_column('users', sa.Column('created_at', sa.DateTime(), 
                                    server_default=sa.text('now()'),
                                    nullable=False))

def downgrade() -> None:
    # Remove created_at column
    op.drop_column('users', 'created_at') 