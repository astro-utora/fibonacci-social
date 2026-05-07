from sqlalchemy import Column, String, ForeignKey, DateTime, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import uuid

class FilloutSubmission(Base):
    __tablename__ = "fillout_submissions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)
    fillout_id = Column(String, nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    requested_at = Column(DateTime, nullable=True)
    validated_at = Column(DateTime, nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    
    # Relationships
    user = relationship("UserDB", back_populates="fillout_submissions")
    project = relationship("Project", back_populates="fillout_submissions")
    
    # Define unique constraint to ensure one record per user per form per project
    __table_args__ = (
        UniqueConstraint('user_id', 'fillout_id', 'project_id', name='uq_fillout_submissions_user_form_project'),
    )

class FilloutData(Base):
    __tablename__ = "fillout_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)
    form_id = Column(String, nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey('projects.id', ondelete='CASCADE'), nullable=True)
    data = Column(JSONB, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("UserDB", back_populates="fillout_data")
    project = relationship("Project", back_populates="fillout_data")
    
    # Define unique constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'form_id', 'project_id', name='uq_fillout_data_user_form_project'),
    ) 