"""add fillout_data table

Revision ID: 016_add_fillout_data_table
Revises: 015_add_admin_settings_table
Create Date: 2023-03-05 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '016_add_fillout_data_table'
down_revision = '015_add_admin_settings_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'fillout_data',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.uuid'), nullable=False),
        sa.Column('form_id', sa.String(), nullable=False),
        sa.Column('data', JSONB, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False, onupdate=sa.func.now()),
        sa.UniqueConstraint('user_id', 'form_id', name='uq_fillout_data_user_form')
    )
    
    op.create_index(
        'ix_fillout_data_user_id',
        'fillout_data',
        ['user_id']
    )
    
    op.create_index(
        'ix_fillout_data_form_id',
        'fillout_data',
        ['form_id']
    )

def downgrade() -> None:
    op.drop_table('fillout_data') 