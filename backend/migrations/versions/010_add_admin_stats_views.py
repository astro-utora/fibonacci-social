"""add admin stats views

Revision ID: 010_add_admin_stats_views
Revises: 009_role_id
Create Date: 2024-02-19 04:15:12.442

"""
from alembic import op
import sqlalchemy as sa

revision = '010_add_admin_stats_views'
down_revision = '009_role_id'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create view for active users
    op.execute("""
        CREATE OR REPLACE VIEW active_users AS
        SELECT COUNT(DISTINCT user_id) as count
        FROM questionnaire_responses;
    """)
    
    # Create view for questionnaire stats
    op.execute("""
        CREATE OR REPLACE VIEW questionnaire_stats AS
        SELECT 
            COUNT(*) as total_questionnaires,
            COUNT(CASE WHEN submitted_at IS NOT NULL THEN 1 END) as completed_questionnaires
        FROM questionnaire_responses;
    """)

def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS active_users;")
    op.execute("DROP VIEW IF EXISTS questionnaire_stats;") 