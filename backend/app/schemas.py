from .schemas.base import *
from .schemas.auth import *
from .schemas.users import *
from .schemas.roles import *
from .schemas.questionnaires import *

from typing import Optional, List, Any
from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

# Base Models
# Request Models

# Additional Request/Response Models
class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    workplace: Optional[str] = None
    birth_date: Optional[str] = None
    goals: Optional[str] = None
    education: Optional[str] = None
    phone_number: Optional[str] = None

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: User

    class Config:
        from_attributes = True
