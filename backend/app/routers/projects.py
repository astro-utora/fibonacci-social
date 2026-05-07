from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel
import uuid
from datetime import datetime

from app.database import get_db
from app.routers.users import get_current_user
from app.models import Project, ProjectMember, UserDB, EmailUser, AuthUser

from app.services.role_tree import update_role_tree, get_role_tree

router = APIRouter()

# Pydantic models for request/response
class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None
    allow_guests: Optional[bool] = False

class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None
    allow_guests: Optional[bool] = None

class ProjectMemberCreate(BaseModel):
    user_id: str
    role: str = "member"

class ProjectMemberResponse(BaseModel):
    id: str
    project_id: str
    user_id: str
    role: str
    created_at: str
    user_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class ProjectResponse(BaseModel):
    id: str
    project_name: str
    description: Optional[str]
    created_at: str
    updated_at: str
    owner_id: str
    allow_guests: bool
    
    class Config:
        from_attributes = True

class ProjectListResponse(BaseModel):
    projects: List[ProjectResponse]

class SingleProjectResponse(BaseModel):
    project: ProjectResponse

class RoleTreeRequest(BaseModel):
    root: Dict[str, Any]

class RoleTreesRequest(BaseModel):
    roots: List[Dict[str, Any]]

class SuccessResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class ProjectSettingResponse(BaseModel):
    key: str
    value: str
    description: str

class ProjectSettingsResponse(BaseModel):
    settings: List[ProjectSettingResponse]

class ProjectSettingUpdate(BaseModel):
    value: str

# Utility function to format a project as ProjectResponse
def format_project_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=str(project.id),
        project_name=project.project_name,
        description=project.description,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        owner_id=str(project.owner_id),
        allow_guests=project.allow_guests
    )

# Project endpoints
@router.post("", response_model=SingleProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new project owned by the current user"""
    project = Project(
        id=str(uuid.uuid4()),
        project_name=project_data.project_name,
        description=project_data.description,
        owner_id=current_user.uuid,
        allow_guests=project_data.allow_guests
    )
    
    db.add(project)
    db.commit()
    db.refresh(project)
    
    # Return the created project in expected format
    return {"project": format_project_response(project)}

@router.get("", response_model=ProjectListResponse)
async def get_user_projects(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all projects where the current user is the owner or a member"""
    # Query projects owned by the user
    owned_projects = db.query(Project).filter(
        Project.owner_id == current_user.uuid
    ).all()
    
    # Query projects where the user is a member
    member_projects_query = db.query(Project).join(
        ProjectMember, 
        ProjectMember.project_id == Project.id
    ).filter(
        ProjectMember.user_id == current_user.uuid
    )
    
    member_projects = member_projects_query.all()
    
    # Combine both lists and remove duplicates
    all_projects = list({project.id: project for project in owned_projects + member_projects}.values())
    
    # Return projects in expected format
    return {"projects": [format_project_response(project) for project in all_projects]}

@router.get("/{project_id}", response_model=SingleProjectResponse)
async def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific project if the user has access"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user is the owner
    if project.owner_id == current_user.uuid:
        return {"project": format_project_response(project)}
    
    # Check if user is a member
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.uuid
    ).first()
    
    if not is_member:
        raise HTTPException(status_code=403, detail="Access denied to this project")
    
    return {"project": format_project_response(project)}

@router.put("/{project_id}", response_model=SingleProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update an existing project"""
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission (owner or admin)
    if str(project.owner_id) != str(current_user.uuid):
        # Check if the user is an admin of the project
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid,
            ProjectMember.role == "admin"
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=403, 
                detail="You do not have permission to update this project"
            )
    
    # Update fields
    if project_data.project_name is not None:
        project.project_name = project_data.project_name
    
    if project_data.description is not None:
        project.description = project_data.description
        
    if project_data.allow_guests is not None:
        project.allow_guests = project_data.allow_guests
    
    db.commit()
    db.refresh(project)
    
    return {"project": format_project_response(project)}

@router.delete("/{project_id}", response_model=SuccessResponse)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a project if the user is the owner"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only the owner can delete the project
    if project.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Only the project owner can delete it")
    
    # Delete the project
    db.delete(project)
    db.commit()
    
    return {"success": True, "message": "Project deleted successfully"}

# Project selection endpoints - these manage the active project in user session
@router.post("/{project_id}/select", response_model=SuccessResponse)
async def select_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Select a project for the current user session"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the project
    if project.owner_id != current_user.uuid:
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid
        ).first()
        
        if not is_member:
            raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Here we would set the active project in the user's session
    # This would depend on your session management implementation
    # For now, we'll just return success
    
    return {"success": True, "message": "Project selected successfully"}

@router.post("/close", response_model=SuccessResponse)
async def close_project(
    current_user = Depends(get_current_user)
):
    """Close the currently selected project"""
    # Here we would clear the active project from the user's session
    # This would depend on your session management implementation
    # For now, we'll just return success
    
    return {"success": True, "message": "Project closed successfully"}

# Project role tree endpoints
@router.post("/{project_id}/role-tree", response_model=SuccessResponse)
async def save_project_role_tree(
    project_id: str,
    tree_data: Union[RoleTreeRequest, RoleTreesRequest],
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Save role tree(s) for a specific project
    
    Request body can have either:
    - A single root: {"root": {...}}
    - Multiple roots: {"roots": [{...}, {...}, ...]}
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only the owner can update the role tree
    if project.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Only the project owner can update the role tree")
    
    try:
        # Forward to the role_tree service, handling both single and multiple tree formats
        if hasattr(tree_data, "root"):
            # Single tree format
            updated_trees = update_role_tree(db, tree_data.root, project_id)
            return {"success": True, "message": "Role tree saved successfully"}
        elif hasattr(tree_data, "roots"):
            # Multiple trees format
            updated_trees = update_role_tree(db, tree_data.roots, project_id)
            return {"success": True, "message": "Role trees saved successfully"}
        else:
            raise ValueError("Request must contain either 'root' or 'roots'")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to save role tree: {str(e)}")

@router.get("/{project_id}/role-tree")
async def get_project_role_tree(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get role tree(s) for a specific project
    
    Response will have either:
    - A single root: {"root": {...}} (if only one tree exists)
    - Multiple roots: {"roots": [{...}, {...}, ...]} (if multiple trees exist)
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the project
    if project.owner_id != current_user.uuid:
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid
        ).first()
        
        if not is_member:
            raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get the role trees using the role_tree service
    trees = get_role_tree(db, project_id)
    
    if not trees:
        # Return an empty tree if none exists
        return {"root": {"role": "Root", "subroles": []}}
    
    # If there's only one tree, return it directly (for backward compatibility)
    if len(trees) == 1:
        return {"root": trees[0]}
    
    # If there are multiple trees, return them as an array
    return {"roots": trees}

@router.get("/{project_id}/users")
async def get_project_users(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get users associated with a project (for getProjectUsers function)"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the project
    if project.owner_id != current_user.uuid:
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid
        ).first()
        
        if not is_member:
            raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get all project users (including owner)
    members = db.query(ProjectMember, UserDB).join(
        UserDB, UserDB.uuid == ProjectMember.user_id
    ).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    # Also include the owner
    owner = db.query(UserDB).filter(UserDB.uuid == project.owner_id).first()
    
    # Format the response to include necessary user info
    users = []
    
    # Add owner with special role
    if owner:
        users.append({
            "id": str(owner.uuid),
            "name": owner.name,
            "email": getattr(owner, 'email', None),  # Owner may not have direct email attribute
            "role": "owner",
            "last_active": owner.created_at.isoformat()
        })
    
    # Add members
    for member, user in members:
        users.append({
            "id": str(user.uuid),
            "name": user.name,
            "email": getattr(user, 'email', None),  # User may not have direct email attribute
            "role": member.role,
            "last_active": user.created_at.isoformat()  # Using created_at as a placeholder
        })
    
    return {"users": users}

# Project members endpoints
@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
async def add_project_member(
    project_id: str,
    member_data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Add a user as a member to a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only the owner can add members
    if project.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Only the project owner can add members")
    
    # Check if the user exists
    user = db.query(UserDB).filter(UserDB.uuid == member_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if the user is already a member
    existing_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == member_data.user_id
    ).first()
    
    if existing_member:
        raise HTTPException(status_code=400, detail="User is already a member of this project")
    
    # Add the user as a member
    member = ProjectMember(
        id=str(uuid.uuid4()),
        project_id=project_id,
        user_id=member_data.user_id,
        role=member_data.role
    )
    
    db.add(member)
    db.commit()
    db.refresh(member)
    
    # Get the user's email
    email_result = db.query(EmailUser.email).join(
        AuthUser, AuthUser.id == EmailUser.auth_id
    ).filter(
        AuthUser.user_uuid == member_data.user_id
    ).first()
    
    email = email_result.email if email_result else None
    
    return ProjectMemberResponse(
        id=str(member.id),
        project_id=str(member.project_id),
        user_id=str(member.user_id),
        role=member.role,
        created_at=member.created_at.isoformat(),
        user_name=user.name,
        email=email
    )

@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def get_project_members(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all members of a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the project
    if project.owner_id != current_user.uuid:
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid
        ).first()
        
        if not is_member:
            raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Get all members
    members = db.query(
        ProjectMember, 
        UserDB.name,
        EmailUser.email
    ).join(
        UserDB, UserDB.uuid == ProjectMember.user_id
    ).join(
        AuthUser, AuthUser.user_uuid == UserDB.uuid
    ).join(
        EmailUser, EmailUser.auth_id == AuthUser.id
    ).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    return [ProjectMemberResponse(
        id=str(member.ProjectMember.id),
        project_id=str(member.ProjectMember.project_id),
        user_id=str(member.ProjectMember.user_id),
        role=member.ProjectMember.role,
        created_at=member.ProjectMember.created_at.isoformat(),
        user_name=member.name,
        email=member.email
    ) for member in members]

@router.delete("/{project_id}/members/{member_id}", response_model=SuccessResponse)
async def remove_project_member(
    project_id: str,
    member_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove a member from a project"""
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Only the owner can remove members
    if project.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Only the project owner can remove members")
    
    # Find the member
    member = db.query(ProjectMember).filter(
        ProjectMember.id == member_id,
        ProjectMember.project_id == project_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Remove the member
    db.delete(member)
    db.commit()
    
    return {"success": True, "message": "Member removed successfully"}

@router.get("/{project_id}/settings", response_model=ProjectSettingsResponse)
async def get_project_settings(
    project_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get all settings for a project"""
    # Check if project exists and if user has access
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has access to the project
    has_access = project.owner_id == current_user.uuid or ProjectMember.is_member(db, project_id, current_user.uuid)
    
    if not has_access:
        raise HTTPException(status_code=403, detail="You do not have access to this project")
    
    # Return project settings
    settings = [
        ProjectSettingResponse(
            key="project_name",
            value=project.project_name,
            description="The name of the project"
        ),
        ProjectSettingResponse(
            key="allow_guests",
            value=str(project.allow_guests).lower(),
            description="Whether guests are allowed to access the project"
        ),
        ProjectSettingResponse(
            key="created_at",
            value=project.created_at.isoformat(),
            description="When the project was created"
        )
    ]
    
    return ProjectSettingsResponse(settings=settings)

@router.patch("/{project_id}/settings/{setting_key}", response_model=ProjectSettingResponse)
async def update_project_setting(
    project_id: str,
    setting_key: str,
    setting_data: ProjectSettingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a specific project setting"""
    # Check if project exists
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check if user has permission (owner or admin)
    if str(project.owner_id) != str(current_user.uuid):
        member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid,
            ProjectMember.role == "admin"
        ).first()
        
        if not member:
            raise HTTPException(
                status_code=403, 
                detail="You do not have permission to update project settings"
            )
    
    # Update the setting based on the key
    description = ""
    
    if setting_key == "project_name":
        project.project_name = setting_data.value
        description = "The name of the project"
    elif setting_key == "allow_guests":
        # Convert string to boolean
        value = setting_data.value.lower()
        if value not in ["true", "false"]:
            raise HTTPException(
                status_code=400, 
                detail="Value for allow_guests must be 'true' or 'false'"
            )
        
        project.allow_guests = value == "true"
        description = "Whether guests are allowed to access the project"
    else:
        raise HTTPException(status_code=404, detail=f"Setting '{setting_key}' not found")
    
    db.commit()
    db.refresh(project)
    
    # Return the updated setting
    return ProjectSettingResponse(
        key=setting_key,
        value=setting_data.value,
        description=description
    ) 