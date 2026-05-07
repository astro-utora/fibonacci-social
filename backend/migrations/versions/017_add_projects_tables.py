"""add projects tables

Revision ID: 017_add_projects_tables
Revises: 016_add_fillout_data_table
Create Date: 2023-03-05 20:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '017_add_projects_tables'
down_revision = '016_add_fillout_data_table'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('project_name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('owner_id', UUID(as_uuid=True), nullable=False),
        sa.Column('allow_guests', sa.Boolean(), server_default='false', nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.uuid'], name='fk_projects_owner_id_users'),
    )
    
    op.create_index('ix_projects_owner_id', 'projects', ['owner_id'])
    
    # Create project_members table for project access control
    op.create_table(
        'project_members',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column('project_id', UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='member'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], name='fk_project_members_project_id_projects', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], name='fk_project_members_user_id_users', ondelete='CASCADE'),
        sa.UniqueConstraint('project_id', 'user_id', name='uq_project_members_project_user')
    )
    
    op.create_index('ix_project_members_project_id', 'project_members', ['project_id'])
    op.create_index('ix_project_members_user_id', 'project_members', ['user_id'])
    
    # Add project_id column to fillout_data table
    op.add_column('fillout_data', 
        sa.Column('project_id', UUID(as_uuid=True), nullable=True)
    )
    
    op.create_foreign_key(
        'fk_fillout_data_project_id_projects',
        'fillout_data', 'projects',
        ['project_id'], ['id'], 
        ondelete='CASCADE'
    )
    
    op.create_index('ix_fillout_data_project_id', 'fillout_data', ['project_id'])

    # Add project_id column to role_nodes table
    op.add_column('role_nodes', 
        sa.Column('project_id', UUID(as_uuid=True), nullable=True)
    )
    
    op.create_foreign_key(
        'fk_role_nodes_project_id_projects',
        'role_nodes', 'projects',
        ['project_id'], ['id'], 
        ondelete='CASCADE'
    )
    
    op.create_index('ix_role_nodes_project_id', 'role_nodes', ['project_id'])

    # Add project_id column to fillout_submissions table
    op.add_column('fillout_submissions', 
        sa.Column('project_id', UUID(as_uuid=True), nullable=True)
    )
    
    op.create_foreign_key(
        'fk_fillout_submissions_project_id_projects',
        'fillout_submissions', 'projects',
        ['project_id'], ['id'], 
        ondelete='CASCADE'
    )
    
    op.create_index('ix_fillout_submissions_project_id', 'fillout_submissions', ['project_id'])

def downgrade() -> None:
    # Remove indexes and foreign keys
    op.drop_index('ix_fillout_submissions_project_id', table_name='fillout_submissions')
    op.drop_constraint('fk_fillout_submissions_project_id_projects', 'fillout_submissions', type_='foreignkey')
    op.drop_column('fillout_submissions', 'project_id')
    
    op.drop_index('ix_fillout_data_project_id', table_name='fillout_data')
    op.drop_constraint('fk_fillout_data_project_id_projects', 'fillout_data', type_='foreignkey')
    op.drop_column('fillout_data', 'project_id')
    
    op.drop_index('ix_project_members_user_id', table_name='project_members')
    op.drop_index('ix_project_members_project_id', table_name='project_members')
    op.drop_table('project_members')
    
    op.drop_index('ix_projects_owner_id', table_name='projects')
    op.drop_table('projects')

    # Remove indexes and foreign keys for role_nodes
    op.drop_index('ix_role_nodes_project_id', table_name='role_nodes')
    op.drop_constraint('fk_role_nodes_project_id_projects', 'role_nodes', type_='foreignkey')
    op.drop_column('role_nodes', 'project_id') 