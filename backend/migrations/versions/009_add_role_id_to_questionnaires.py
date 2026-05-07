"""add role_id to questionnaires

Revision ID: 009_role_id
Revises: 008_add_created_at_to_users
Create Date: 2024-02-19 04:21:44.231

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = '009_role_id'
down_revision: Union[str, None] = '008_add_created_at_to_users'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Add role_id column with foreign key constraint
    op.add_column('questionnaires', 
        sa.Column('role_id', UUID(as_uuid=True), 
                 sa.ForeignKey('roles.id', ondelete='CASCADE'),
                 nullable=False))
    
    # Add index for faster lookups
    op.create_index('ix_questionnaires_role_id', 'questionnaires', ['role_id'])

def downgrade() -> None:
    # Remove index and column
    op.drop_index('ix_questionnaires_role_id')
    op.drop_column('questionnaires', 'role_id') 