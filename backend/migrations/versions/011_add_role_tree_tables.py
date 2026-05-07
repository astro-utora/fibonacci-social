"""add role tree tables

Revision ID: 011_add_role_tree_tables
Revises: 010_add_admin_stats_views
Create Date: 2024-xx-xx
"""
from alembic import op
import sqlalchemy as sa

revision = '011_add_role_tree_tables'
down_revision = '010_add_admin_stats_views'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create role_nodes table
    op.create_table(
        'role_nodes',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('fillout_id', sa.String(), nullable=True),
        sa.Column('parent_id', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['role_nodes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index
    op.create_index(op.f('ix_role_nodes_parent_id'), 'role_nodes', ['parent_id'], unique=False)

def downgrade() -> None:
    # Drop index
    op.drop_index(op.f('ix_role_nodes_parent_id'), table_name='role_nodes')

    # Drop table
    op.drop_table('role_nodes') 