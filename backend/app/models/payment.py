from sqlalchemy import Column, String, ForeignKey, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
from uuid import uuid4

class Payment(Base):
    """Database model for payment records"""
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False)
    payment_id = Column(String, nullable=True, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='SET NULL'), nullable=True)
    total_amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    
    # Relationships
    user = relationship("UserDB", back_populates="payments") 