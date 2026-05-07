from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import UserDB, InvitationDB
from ..schemas import InvitationCreate, InvitationResponse
from .users import get_current_user
from uuid import UUID
from datetime import datetime
from typing import Optional

router = APIRouter()

@router.post("", response_model=InvitationResponse)
async def create_invitation(
    invitation: InvitationCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    try:
        print(f"invitation: {invitation}")

        # Create new invitation record
        db_invitation = InvitationDB(
            name=invitation.name,
            location=invitation.location,
            workplace=invitation.workplace,
            role=invitation.role,
            birth_date=invitation.birth_date,
            goals=invitation.goals,
            education=invitation.education,
            phone_number=invitation.phone_number,
            referral=current_user.uuid,
            status="pending",
            created_at=datetime.utcnow()
        )
        
        db.add(db_invitation)
        db.commit()
        db.refresh(db_invitation)

        # Convert to Pydantic model before returning
        return db_invitation
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=400, detail="Could not create invitation")

@router.get("/{invitation_id}")
async def get_invitation(invitation_id: UUID, db: Session = Depends(get_db)):
    """Get invitation data by ID"""
    invitation = db.query(InvitationDB).filter(
        InvitationDB.id == invitation_id,
        InvitationDB.status == "pending"
    ).first()
    
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already used")
        
    return invitation 