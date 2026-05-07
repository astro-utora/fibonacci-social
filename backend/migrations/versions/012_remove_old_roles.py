"""remove old roles

Revision ID: 012_remove_old_roles
Revises: 011_add_role_tree_tables
Create Date: 2024-01-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '012_remove_old_roles'
down_revision = '011_add_role_tree_tables'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Drop dependent views first
    op.execute('DROP VIEW IF EXISTS active_users CASCADE')
    op.execute('DROP VIEW IF EXISTS questionnaire_stats CASCADE')
    
    # Then drop dependent tables
    op.drop_table('questionnaire_responses')
    op.drop_table('questionnaires')
    op.drop_table('roles')

def downgrade() -> None:
    # Recreate tables in reverse order
    op.create_table(
        'roles',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
    )
        
    op.create_table(
        'questionnaires',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('role_id', sa.String(), sa.ForeignKey('roles.id')),
    )
    
    op.create_table(
        'questionnaire_responses',
        sa.Column('id', sa.UUID(), primary_key=True),
        sa.Column('user_id', sa.UUID(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('questionnaire_id', sa.String(), sa.ForeignKey('questionnaires.id'), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    
    # Recreate views if needed
    op.execute("""
        CREATE VIEW active_users AS
        SELECT DISTINCT user_id 
        FROM questionnaire_responses
        WHERE created_at >= NOW() - INTERVAL '30 days'
    """)
    
    op.execute("""
        CREATE VIEW questionnaire_stats AS
        SELECT 
            questionnaire_id,
            COUNT(*) as response_count,
            MAX(created_at) as last_response
        FROM questionnaire_responses
        GROUP BY questionnaire_id
    """) 