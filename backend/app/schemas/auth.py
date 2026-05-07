from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from ..schemas.users import User

class EmailRegister(BaseModel):
    """Schema for email registration"""
    email: EmailStr
    password: str
    invitation_id: Optional[UUID] = None
    referral: Optional[str] = None

class EmailLogin(BaseModel):
    """Schema for email login"""
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: User

    class Config:
        from_attributes = True

class InvitationCreate(BaseModel):
    name: str
    location: str
    workplace: str
    role: str
    birth_date: str
    goals: str
    education: str
    phone_number: str
    referral: Optional[str] = None

class InvitationResponse(BaseModel):
    id: UUID
    name: str
    location: str
    workplace: str
    role: str
    birth_date: str
    goals: str
    education: str
    phone_number: str
    referral: Optional[UUID]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True 