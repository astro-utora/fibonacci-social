from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AdminStats(BaseModel):
    total_users: int

class AdminSettingBase(BaseModel):
    key: str
    value: str
    description: Optional[str] = None

class AdminSettingCreate(AdminSettingBase):
    pass

class AdminSettingUpdate(BaseModel):
    value: str
    description: Optional[str] = None

class AdminSetting(AdminSettingBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

