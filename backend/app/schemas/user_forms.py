from pydantic import BaseModel
from typing import Optional, List
from ..schemas.users import PaginationMeta

class UserFormEntry(BaseModel):
    """
    Schema representing a user's form entry for admin monitoring.
    """
    id: str
    userId: str
    userName: Optional[str] = None
    role: Optional[str] = None
    filloutId: str
    startDate: Optional[str] = None
    completeDate: Optional[str] = None
    requestedDate: Optional[str] = None
    validatedDate: Optional[str] = None
    
    class Config:
        orm_mode = True 

class PaginatedUserFormResponse(BaseModel):
    """Schema for paginated user form response"""
    items: List[UserFormEntry]
    pagination: PaginationMeta 