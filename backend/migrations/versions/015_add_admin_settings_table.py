"""Add admin settings table

Revision ID: 015_add_admin_settings_table
Revises: 014_add_payments_table
Create Date: 2023-10-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '015_add_admin_settings_table'
down_revision = '014_add_payments_table'
branch_labels = None
depends_on = None


def upgrade():
    # Create admin_settings table
    op.create_table(
        'admin_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_settings_id'), 'admin_settings', ['id'], unique=False)
    op.create_index(op.f('ix_admin_settings_key'), 'admin_settings', ['key'], unique=True)
    
    # Insert default filloutOnboardingId
    op.execute(
        """
        INSERT INTO admin_settings (key, value, description)
        VALUES ('filloutOnboardingId', '6DzLtyFsoXus', 'Fillout form ID used for user onboarding')
        """
    )


def downgrade():
    op.drop_index(op.f('ix_admin_settings_key'), table_name='admin_settings')
    op.drop_index(op.f('ix_admin_settings_id'), table_name='admin_settings')
    op.drop_table('admin_settings') 