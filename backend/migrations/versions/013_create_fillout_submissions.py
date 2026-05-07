"""create fillout submissions

Revision ID: 013_create_fillout_submissions
Revises: 012_remove_old_roles
Create Date: 2025-02-20 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = '013_create_fillout_submissions'
down_revision = '012_remove_old_roles'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'fillout_submissions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.uuid'), nullable=False),
        sa.Column('fillout_id', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
    )
    
    op.create_index(
        'ix_fillout_submissions_user_id',
        'fillout_submissions',
        ['user_id']
    )

def downgrade() -> None:
    op.drop_table('fillout_submissions') 