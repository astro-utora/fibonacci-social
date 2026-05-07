"""create user roles and referral codes

Revision ID: 002_roles_refs
Revises: 001_initial
Create Date: 2024-03-21

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic
revision = '002_roles_refs'
down_revision = '001_initial'
branch_labels = None
depends_on = None

def upgrade():
    # Enable pgcrypto extension for gen_random_bytes
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('role', sa.String(), nullable=False, server_default='user'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['user_id'], ['users.uuid'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role', name='unique_user_role')
    )
    op.create_index(op.f('ix_user_roles_id'), 'user_roles', ['id'], unique=False)

    # Add referral_code to users table
    op.add_column('users', 
        sa.Column('referral_code', sa.String(), nullable=True, unique=True)
    )
    
    # Add referral_id as foreign key to users table
    op.add_column('users',
        sa.Column('referral_id', sa.UUID(), nullable=True)
    )
    op.create_foreign_key(
        'fk_users_referral',
        'users', 'users',
        ['referral_id'], ['uuid'],
        ondelete='SET NULL'
    )
    
    # Create a connection to execute SQL
    connection = op.get_bind()
    
    # Generate and update referral codes for existing users
    connection.execute(
        sa.text("""
        UPDATE users 
        SET referral_code = substr(encode(gen_random_bytes(8), 'base64'), 1, 11)
        WHERE referral_code IS NULL
        """)
    )
    
    # Convert existing referral strings to referral_id if they match UUIDs
    connection.execute(
        sa.text("""
        UPDATE users u1
        SET referral_id = u2.uuid
        FROM users u2
        WHERE u1.referral = u2.uuid::text
        """)
    )
    
    # Make the referral_code column non-nullable after populating
    op.alter_column('users', 'referral_code',
        existing_type=sa.String(),
        nullable=False
    )
    
    # Drop the old referral column
    op.drop_column('users', 'referral')

    # Add invitations table
    op.create_table(
        'invitations',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('location', sa.String(), nullable=False),
        sa.Column('role', sa.String(), nullable=False),
        sa.Column('workplace', sa.String(), nullable=False),
        sa.Column('birth_date', sa.String(), nullable=False),
        sa.Column('goals', sa.String(), nullable=False),
        sa.Column('education', sa.String(), nullable=False),
        sa.Column('phone_number', sa.String(), nullable=False),
        sa.Column('referral', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['referral'], ['users.uuid'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    # Add back the old referral column
    op.add_column('users',
        sa.Column('referral', sa.String(), nullable=True)
    )
    
    # Convert referral_id back to referral string
    connection = op.get_bind()
    connection.execute(
        sa.text("""
        UPDATE users u1
        SET referral = u2.uuid::text
        FROM users u2
        WHERE u1.referral_id = u2.uuid
        """)
    )
    
    # Remove new columns and constraints
    op.drop_constraint('fk_users_referral', 'users')
    op.drop_column('users', 'referral_id')
    op.drop_constraint("uq_users_referral_code", "users")
    op.drop_column('users', 'referral_code')
    
    # Remove user_roles table
    op.drop_index(op.f('ix_user_roles_id'), table_name='user_roles')
    op.drop_table('user_roles')
    
    # Drop the pgcrypto extension at the end
    op.execute('DROP EXTENSION IF EXISTS "pgcrypto"')

    # Drop invitations table
    op.drop_table('invitations') 