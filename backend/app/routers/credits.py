from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.database import get_db
from app.routers.users import get_current_user
from app.models.base import UserDB
from app.services import credits as credits_service

router = APIRouter()

class CreditsResponse(BaseModel):
    user_uuid: str
    credits: int
    
    class Config:
        from_attributes = True

class CreditsUpdateRequest(BaseModel):
    amount: int

@router.get("", response_model=CreditsResponse)
async def get_credits(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Get credits for the current user"""
    credits = credits_service.get_user_credits(db, current_user.uuid)
    
    if not credits:
        # This should never happen as get_user_credits creates a record if one doesn't exist
        raise HTTPException(status_code=404, detail="Credits not found")
        
    return CreditsResponse(user_uuid=str(current_user.uuid), credits=credits.credits)


# Admin routes for managing credits
@router.post("/admin/set/{user_uuid}", response_model=CreditsResponse)
async def admin_set_credits(
    user_uuid: str,
    data: CreditsUpdateRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Set credits for a specific user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
        
    if data.amount < 0:
        raise HTTPException(status_code=400, detail="Amount cannot be negative")
        
    credits = credits_service.set_user_credits(db, user_uuid, data.amount)
    
    if not credits:
        raise HTTPException(status_code=404, detail="User not found or failed to update credits")
        
    return credits 