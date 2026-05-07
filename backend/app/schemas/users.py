from typing import Optional, List, ForwardRef
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from .roles import RoleResponse

# Base User model without relationships
class User(BaseModel):
    uuid: UUID
    name: Optional[str] = None
    location: Optional[str] = None
    workplace: Optional[str] = None
    role: Optional[str] = None
    birth_date: Optional[str] = None
    goals: Optional[str] = None
    education: Optional[str] = None
    phone_number: Optional[str] = None
    referral_code: Optional[str] = None
    avatar_url: Optional[str] = None
    willing_to_contribute: Optional[bool] = None
    is_admin: bool = False
    payment_status: Optional[str] = None
    credits: Optional[int] = 0
    waiting_list_status: Optional[str] = None  # pending, approved, or null if not in waiting list

    class Config:
        from_attributes = True

# Input models
class UserRoleResponse(BaseModel):
    id: int
    role: RoleResponse
    created_at: datetime

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    """Schema for user response"""
    uuid: UUID
    name: Optional[str]
    location: Optional[str]
    workplace: Optional[str]
    birth_date: Optional[str]
    goals: Optional[str]
    education: Optional[str]
    phone_number: Optional[str]
    avatar_url: Optional[str]
    referral_code: str
    roles: List[UserRoleResponse]
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileUpdate(BaseModel):
    """Schema for profile update data"""
    name: Optional[str] = None
    location: Optional[str] = None
    role: Optional[str] = None
    workplace: Optional[str] = None
    birth_date: Optional[str] = None
    goals: Optional[str] = None
    education: Optional[str] = None
    phone_number: Optional[str] = None

class UserProfile(BaseModel):
    """Schema for user profile data"""
    id: str
    name: Optional[str] = None
    location: Optional[str] = None
    workplace: Optional[str] = None
    birth_date: Optional[str] = None
    goals: List[str] = []
    education: Optional[str] = None
    roles: List[str] = []
    avatar_url: Optional[str] = None
    referral_code: str

class WaitingListEntry(BaseModel):
    """Schema for waiting list entry"""
    id: UUID
    user_id: UUID
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WaitingListResponse(BaseModel):
    """Schema for waiting list response with user details"""
    id: UUID
    user_id: UUID
    user_name: Optional[str] = None
    email: Optional[str] = None
    status: str
    created_at: datetime
    approved_at: Optional[datetime] = None

class PaginationMeta(BaseModel):
    """Schema for pagination metadata"""
    page: int
    page_size: int
    total_count: int
    total_pages: int

class PaginatedWaitingListResponse(BaseModel):
    """Schema for paginated waiting list response"""
    items: List[WaitingListResponse]
    pagination: PaginationMeta 