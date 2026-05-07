from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from typing import List, Optional
from datetime import datetime
from uuid import UUID

from ..database import get_db
from ..models import UserDB, WaitingListDB, EmailUser, AuthUser
from ..schemas.users import WaitingListResponse, WaitingListEntry, PaginatedWaitingListResponse
from .auth import is_admin
from .users import get_current_user

router = APIRouter()

@router.get("", response_model=PaginatedWaitingListResponse)
async def get_waiting_list(
    status: Optional[str] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all users in the waiting list.
    Optionally filter by status.
    Supports pagination.
    Only accessible by admins.
    """
    # Check if user is admin
    if not is_admin(current_user, db):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Create base query for waiting list entries
    query = db.query(
        WaitingListDB,
        UserDB.name.label("user_name"),
        EmailUser.email.label("email")
    ).join(
        UserDB, WaitingListDB.user_id == UserDB.uuid
    ).join(
        AuthUser, AuthUser.user_uuid == UserDB.uuid, isouter=True
    ).join(
        EmailUser, EmailUser.auth_id == AuthUser.id, isouter=True
    )
    
    # Apply status filter if provided
    if status:
        query = query.filter(WaitingListDB.status == status)
    
    # Get total count for pagination metadata
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(WaitingListDB.created_at.desc()).offset(offset).limit(page_size)
    
    # Execute query
    results = query.all()
    
    # Transform query results to response schema
    waiting_list_items = [
        WaitingListResponse(
            id=entry.id,
            user_id=entry.user_id,
            user_name=user_name,
            email=email,
            status=entry.status,
            created_at=entry.created_at,
            approved_at=entry.approved_at
        ) for entry, user_name, email in results
    ]
    
    # Return paginated response
    return {
        "items": waiting_list_items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    }

@router.post("/{user_id}/approve", response_model=WaitingListEntry)
async def approve_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Approve a user from the waiting list.
    Only accessible by admins.
    """
    # Check if user is admin
    if not is_admin(current_user, db):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find the waiting list entry
    entry = db.query(WaitingListDB).filter(
        WaitingListDB.user_id == user_id,
        WaitingListDB.status == "pending"
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Waiting list entry not found or already processed"
        )
    
    # Update the entry
    entry.status = "approved"
    entry.approved_at = datetime.utcnow()
    
    try:
        db.commit()
        db.refresh(entry)
        return entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error approving user: {str(e)}"
        )

@router.post("/{user_id}/reject", response_model=WaitingListEntry)
async def reject_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Reject a user from the waiting list.
    Only accessible by admins.
    """
    # Check if user is admin
    if not is_admin(current_user, db):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find the waiting list entry
    entry = db.query(WaitingListDB).filter(
        WaitingListDB.user_id == user_id,
        WaitingListDB.status == "pending"
    ).first()
    
    if not entry:
        raise HTTPException(
            status_code=404,
            detail="Waiting list entry not found or already processed"
        )
    
    # Update the entry
    entry.status = "rejected"
    
    try:
        db.commit()
        db.refresh(entry)
        return entry
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error rejecting user: {str(e)}"
        )

@router.get("/status", response_model=Optional[WaitingListEntry])
async def get_current_user_waiting_status(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get the current user's waiting list status.
    """
    entry = db.query(WaitingListDB).filter(
        WaitingListDB.user_id == current_user.uuid
    ).first()
    
    return entry 