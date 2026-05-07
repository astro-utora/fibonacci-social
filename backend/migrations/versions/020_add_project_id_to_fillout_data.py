"""Add project_id to fillout_data table

Revision ID: 020_add_project_id_to_fillout
Revises: 019_add_validation_columns
Create Date: 2025-03-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = '020_add_project_id_to_fillout'
down_revision = '019_add_validation_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Drop the existing unique constraint
    op.drop_constraint('uq_fillout_data_user_form', 'fillout_data', type_='unique')
    
    # Step 2: Add project_id column
    op.add_column('fillout_data', sa.Column('project_id', UUID(as_uuid=True), nullable=True))
    
    # Step 3: Add foreign key constraint
    op.create_foreign_key(
        'fk_fillout_data_project_id',
        'fillout_data', 'projects',
        ['project_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Step 4: Match project_id from fillout_submissions
    # This SQL tries to find a matching fillout_submission for each fillout_data record
    # and updates the project_id to match
    op.execute('''
    UPDATE fillout_data fd
    SET project_id = fs.project_id
    FROM fillout_submissions fs
    WHERE fd.user_id = fs.user_id
    AND fd.form_id = fs.fillout_id
    AND fs.project_id IS NOT NULL
    ''')
    
    # Step 5: Create new unique constraint including project_id
    op.create_unique_constraint(
        'uq_fillout_data_user_form_project',
        'fillout_data',
        ['user_id', 'form_id', 'project_id']
    )
    
    # Create index for performance
    op.create_index(
        'idx_fillout_data_project',
        'fillout_data',
        ['project_id']
    )


def downgrade():
    # Step 1: Drop the new unique constraint
    op.drop_constraint('uq_fillout_data_user_form_project', 'fillout_data', type_='unique')
    
    # Step 2: Drop the index
    op.drop_index('idx_fillout_data_project', table_name='fillout_data')
    
    # Step 3: Drop the foreign key
    op.drop_constraint('fk_fillout_data_project_id', 'fillout_data', type_='foreignkey')
    
    # Step 4: Drop the project_id column
    op.drop_column('fillout_data', 'project_id')
    
    # Step 5: Recreate the original unique constraint
    op.create_unique_constraint(
        'uq_fillout_data_user_form',
        'fillout_data',
        ['user_id', 'form_id']
    ) 