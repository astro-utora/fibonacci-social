from sqlalchemy import Column, String, ForeignKey, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class RoleNode(Base):
    __tablename__ = "role_nodes"

    id = Column(String, primary_key=True)
    role = Column(String, nullable=False)
    fillout_id = Column(String, nullable=True)
    parent_id = Column(String, ForeignKey("role_nodes.id", ondelete="CASCADE"), nullable=True)
    previous_sibling_id = Column(String, ForeignKey("role_nodes.id", ondelete="SET NULL"), nullable=True)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent = relationship("RoleNode", back_populates="subroles", remote_side=[id], foreign_keys=[parent_id])
    subroles = relationship("RoleNode", back_populates="parent", cascade="all, delete-orphan", foreign_keys=[parent_id])
    previous_sibling = relationship("RoleNode", remote_side=[id], foreign_keys=[previous_sibling_id])
    project = relationship("Project", back_populates="role_nodes")
