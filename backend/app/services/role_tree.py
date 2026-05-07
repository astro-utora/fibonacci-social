from typing import Optional, Dict, List, Union
from sqlalchemy.orm import Session
from app.models import RoleNode
from uuid import uuid4
from pydantic import BaseModel, Field, validator

class SubRoleSchema(BaseModel):
    role: str
    filloutId: Optional[str] = None
    subroles: List['SubRoleSchema'] = []

    @validator('role')
    def role_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Role name cannot be empty')
        return v.strip()

class RoleTreeSchema(BaseModel):
    root: SubRoleSchema

def validate_role_tree(tree: Dict) -> None:
    """Validate role tree structure"""
    if not isinstance(tree, dict):
        raise ValueError("Role tree must be a dictionary")
    
    if 'role' not in tree:
        raise ValueError("Each node must have a 'role' field")
    
    if not isinstance(tree['role'], str) or not tree['role'].strip():
        raise ValueError("Role name must be a non-empty string")
    
    if 'filloutId' in tree and not isinstance(tree['filloutId'], (str, type(None))):
        raise ValueError("filloutId must be a string or null")
    
    if 'subroles' in tree:
        if not isinstance(tree['subroles'], list):
            raise ValueError("subroles must be an array")
        
        for subrole in tree['subroles']:
            validate_role_tree(subrole)

def serialize_role_tree(node: RoleNode) -> Dict:
    """Convert RoleNode to dictionary format"""
    # Get all subroles
    all_subroles = list(node.subroles)
    
    # Build an index of id to subrole for O(1) lookups
    id_to_role = {sr.id: sr for sr in all_subroles}
    
    # Also build an index mapping previous_sibling_id to subrole for O(1) lookups
    id_to_next_role = {}
    current = None
    for sr in all_subroles:
        if sr.previous_sibling_id is not None:
            id_to_next_role[sr.previous_sibling_id] = sr
        else:
            current = sr
    
    # Order subroles based on previous_sibling_id
    ordered_subroles = []
    
    # Build the ordered list by following the previous_sibling chain
    while current and len(ordered_subroles) < len(all_subroles):
        ordered_subroles.append(current)
        current_id = current.id
        current = id_to_next_role.get(current_id)
    
    # If there are any remaining subroles (in case of circular references or other issues)
    # append them to the end to avoid data loss
    remaining = [sr for sr in all_subroles if sr not in ordered_subroles]
    ordered_subroles.extend(remaining)
    
    return {
        'role': node.role,
        'filloutId': node.fillout_id,
        'subroles': [serialize_role_tree(child) for child in ordered_subroles]
    }

def save_role_tree(db: Session, tree: Dict, parent_id: Optional[str] = None, project_id: Optional[str] = None, previous_sibling_id: Optional[str] = None) -> RoleNode:
    """
    Save role tree to database
    
    Args:
        db: Database session
        tree: Role tree data
        parent_id: Optional parent node ID
        project_id: Optional project ID for project-specific role trees
        previous_sibling_id: Optional ID of the previous sibling
    """
    # Create new node
    node = RoleNode(
        id=str(uuid4()),
        role=tree['role'],
        fillout_id=tree.get('filloutId'),
        parent_id=parent_id,
        previous_sibling_id=previous_sibling_id,
        project_id=project_id
    )
    db.add(node)
    db.flush()  # Get ID without committing

    # Recursively save subroles
    prev_sibling_id = None
    for subrole in tree.get('subroles', []):
        # Save subrole with current prev_sibling_id
        subrole_node = save_role_tree(db, subrole, node.id, project_id, prev_sibling_id)
        # Update prev_sibling_id for the next iteration
        prev_sibling_id = subrole_node.id
    
    return node

def get_role_tree(db: Session, project_id: Optional[str] = None) -> List[Dict]:
    """
    Get all root role trees
    
    Args:
        db: Database session
        project_id: Optional project ID for project-specific role trees
        
    Returns:
        List of serialized role trees. Each item in the list is a root node.
    """
    # Query for root nodes with optional project_id filter
    query = db.query(RoleNode).filter(RoleNode.parent_id.is_(None))
    
    if project_id is not None:
        query = query.filter(RoleNode.project_id == project_id)
    else:
        query = query.filter(RoleNode.project_id.is_(None))
        
    # Get all root nodes, not just the first one
    roots = query.all()
    
    # Serialize each root node and return as a list
    return [serialize_role_tree(root) for root in roots]

def update_role_tree(db: Session, trees: Union[Dict, List[Dict]], project_id: Optional[str] = None) -> List[Dict]:
    """
    Update role trees
    
    Args:
        db: Database session
        trees: Either a single role tree dictionary or a list of role tree dictionaries
        project_id: Optional project ID for project-specific role trees
        
    Returns:
        List of serialized role trees after update
    """
    # Convert single tree to list for uniform processing
    if isinstance(trees, dict):
        trees = [trees]
    
    # Validate each tree structure
    for tree in trees:
        validate_role_tree(tree)
    
    # Clear existing trees for the given project (or main trees if project_id is None)
    query = db.query(RoleNode)
    
    if project_id is not None:
        query = query.filter(RoleNode.project_id == project_id)
    else:
        query = query.filter(RoleNode.project_id.is_(None))
        
    query.delete(synchronize_session=False)
    
    # Save all new trees
    root_nodes = []
    prev_root_id = None
    for tree in trees:
        # Root nodes can also have siblings (multiple root trees)
        root = save_role_tree(db, tree, project_id=project_id, previous_sibling_id=prev_root_id)
        root_nodes.append(root)
        prev_root_id = root.id
    
    db.commit()
    
    # Return serialized trees
    return [serialize_role_tree(root) for root in root_nodes]
