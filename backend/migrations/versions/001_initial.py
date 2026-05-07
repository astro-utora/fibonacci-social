"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-02-17
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create auth_provider enum type
    auth_provider = sa.Enum('telegram', 'whatsapp', 'google', name='auth_provider')
    auth_provider.create(op.get_bind())

    # Create users table
    op.create_table('users',
        sa.Column('uuid', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=True),
        sa.Column('workplace', sa.String(), nullable=True),
        sa.Column('birth_date', sa.String(), nullable=True),
        sa.Column('goals', sa.String(), nullable=True),
        sa.Column('education', sa.String(), nullable=True),
        sa.Column('referral', sa.String(), nullable=True),
        sa.Column('phone_number', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('uuid')
    )
    op.create_index(op.f('ix_users_uuid'), 'users', ['uuid'], unique=True)

    # Create base auth_users table
    op.create_table('auth_users',
        sa.Column('id', UUID(as_uuid=True), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('user_uuid', UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(['user_uuid'], ['users.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # Create telegram_users table
    op.create_table('telegram_users',
        sa.Column('auth_id', UUID(as_uuid=True), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(['auth_id'], ['auth_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('auth_id')
    )
    op.create_index(op.f('ix_telegram_users_telegram_id'), 'telegram_users', ['telegram_id'], unique=True)

def downgrade():
    op.drop_index(op.f('ix_telegram_users_telegram_id'), table_name='telegram_users')
    op.drop_table('telegram_users')
    op.drop_table('auth_users')
    op.drop_index(op.f('ix_users_uuid'), table_name='users')
    op.drop_table('users')
    # Drop the enum type
    op.execute('DROP TYPE auth_provider') 