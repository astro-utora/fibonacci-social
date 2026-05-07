"""Add questionnaires

Revision ID: 006_questionnaires
Revises: 005_add_avatar
Create Date: 2024-03-22
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = '006_questionnaires'
down_revision = '005_add_avatar'
branch_labels = None
depends_on = None

def upgrade():
    # Create questionnaires table
    op.create_table(
        'questionnaires',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('fields', JSONB, nullable=False),
        sa.Column('created_by', UUID(as_uuid=True), sa.ForeignKey('users.uuid')),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime()),
        sa.PrimaryKeyConstraint('id')
    )

    # Create responses table
    op.create_table(
        'questionnaire_responses',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('questionnaire_id', UUID(as_uuid=True), sa.ForeignKey('questionnaires.id')),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.uuid')),
        sa.Column('answers', JSONB, nullable=False),
        sa.Column('submitted_at', sa.DateTime(), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('questionnaire_responses')
    op.drop_table('questionnaires') 