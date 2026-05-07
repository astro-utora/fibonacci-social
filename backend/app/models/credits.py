from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4

from app.database import Base


class Credits(Base):
    """Credits model to track user credits"""
    __tablename__ = "credits"

    id = Column(UUID, primary_key=True, index=True, default=uuid4)
    user_uuid = Column(UUID, ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    credits = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("UserDB", back_populates="credits")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 