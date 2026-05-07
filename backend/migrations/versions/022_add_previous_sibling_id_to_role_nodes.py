"""Add previous_sibling_id to role_nodes table

Revision ID: 022_add_previous_sibling_id
Revises: 021_add_waiting_list_table
Create Date: 2023-05-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = '022_add_previous_sibling_id'
down_revision = '021_add_waiting_list_table'
branch_labels = None
depends_on = None


def upgrade():
    # Add previous_sibling_id column to role_nodes table
    op.add_column('role_nodes', sa.Column('previous_sibling_id', sa.String(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_role_nodes_previous_sibling',
        'role_nodes', 'role_nodes',
        ['previous_sibling_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Create an index for better performance when querying siblings
    op.create_index('idx_role_nodes_previous_sibling_id', 'role_nodes', ['previous_sibling_id'])
    
    # Update existing role trees to set previous_sibling_id
    connection = op.get_bind()
    
    # First, get all parent nodes that have children
    parent_ids = connection.execute(
        text("SELECT DISTINCT parent_id FROM role_nodes WHERE parent_id IS NOT NULL")
    ).fetchall()
    
    # For each parent, order its children and set previous_sibling_id
    for parent_id_row in parent_ids:
        parent_id = parent_id_row[0]
        
        # Get all children of this parent ordered by ID (or created_at if you prefer)
        children = connection.execute(
            text("SELECT id FROM role_nodes WHERE parent_id = :parent_id ORDER BY id"),
            {"parent_id": parent_id}
        ).fetchall()
        
        # Set previous_sibling_id for each child except the first one
        prev_id = None
        for child_id_row in children:
            child_id = child_id_row[0]
            
            if prev_id is not None:
                # Update this child to point to the previous sibling
                connection.execute(
                    text("UPDATE role_nodes SET previous_sibling_id = :prev_id WHERE id = :child_id"),
                    {"prev_id": prev_id, "child_id": child_id}
                )
            
            prev_id = child_id


def downgrade():
    # Drop foreign key constraint first
    op.drop_constraint('fk_role_nodes_previous_sibling', 'role_nodes', type_='foreignkey')
    
    # Drop index
    op.drop_index('idx_role_nodes_previous_sibling_id', table_name='role_nodes')
    
    # Drop column
    op.drop_column('role_nodes', 'previous_sibling_id')