from typing import Optional
from pydantic import BaseModel, constr
from datetime import datetime
from uuid import UUID
from .base import TimestampedModel

class RoleBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    label: constr(min_length=1, max_length=100)
    description: Optional[str] = None

class RoleCreate(RoleBase):
    pass

class RoleUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    label: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None

class RoleResponse(RoleBase):
    id: UUID
    created_by: Optional[UUID] = None
    questionnaires: list = []

    class Config:
        from_attributes = True 