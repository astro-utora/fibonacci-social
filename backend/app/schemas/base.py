from typing import Optional, List, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID

# Common base models that are used across multiple domains
class TimestampedModel(BaseModel):
    created_at: datetime

    class Config:
        from_attributes = True 