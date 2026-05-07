from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from pydantic import BaseModel

from app.database import get_db
from app.routers.users import get_current_user
from app.models import Project, ProjectMember, RoleNode, UserDB
from app.services.role_tree import get_role_tree, update_role_tree, validate_role_tree

router = APIRouter()

class SubRole(BaseModel):
    role: str
    filloutId: Optional[str] = None
    subroles: List['SubRole'] = []

class RoleTreeUpdate(BaseModel):
    root: SubRole

class RoleTreesUpdate(BaseModel):
    roots: List[SubRole]

def validate_project_owner(project_id: str, current_user: UserDB, db: Session, error_message: str):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail=error_message)

@router.get("")
async def get_role_tree_endpoint(
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get role tree for user.
    If project_id is provided, returns the project-specific role trees.
    If project_id is None, returns the main role trees.
    """
    # Check project access if project_id is provided
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Check if user is a member of the project
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid
        ).first()
        
        if not is_member and project.owner_id != current_user.uuid:
            raise HTTPException(status_code=403, detail="Access denied to this project")

    # Query the role trees using the service function
    trees = get_role_tree(db, project_id)
    
    if not trees:
        # Return an empty tree if none exists
        return {"root": {"role": "Root", "subroles": []}}
    
    # If there's only one tree, return it directly (for backward compatibility)
    if len(trees) == 1:
        return {"root": trees[0]}
    
    # If there are multiple trees, return them as an array
    return {"roots": trees}

@router.post("")
async def update_role_tree_endpoint(
    tree_data: Dict,
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update role trees for user.
    If project_id is provided, updates the project-specific role trees.
    If project_id is None, updates the main role trees.
    
    Request body can have either:
    - A single root: {"root": {...}}
    - Multiple roots: {"roots": [{...}, {...}, ...]}
    """
    # Check project access if project_id is provided
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Only project owner can update the role tree
        validate_project_owner(project_id, current_user, db, "Only the project owner can update the role tree")
    try:
        trees_to_update = []

        # Handle both single tree and multiple trees formats
        if "root" in tree_data:
            # Single tree format
            if "roots" in tree_data:
                raise ValueError("Cannot provide both 'root' and 'roots' in the same request")
            trees_to_update = [tree_data["root"]]
        elif "roots" in tree_data:
            # Multiple trees format
            if not isinstance(tree_data["roots"], list):
                raise ValueError("'roots' must be an array")
            trees_to_update = tree_data["roots"]
        else:
            raise ValueError("Request must contain either 'root' or 'roots'")
        
        # Update trees
        updated_trees = update_role_tree(db, trees_to_update, project_id)
        
        # Format response according to the input format
        if "root" in tree_data:
            # Return single tree format for backward compatibility
            return {"success": True, "root": updated_trees[0] if updated_trees else None}
        else:
            # Return multiple trees format
            return {"success": True, "roots": updated_trees}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update role tree: {str(e)}") 