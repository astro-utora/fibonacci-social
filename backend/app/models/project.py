import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from app.database import Base  # Import Base from database instead of creating a new one
from app.models.base import UserDB  # Import UserDB to avoid circular imports
import sqlalchemy as sa


class Project(Base):
    """
    Project model for storing project information.
    One project can have multiple members (users) with different roles.
    """
    __tablename__ = "projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"), nullable=False)
    allow_guests = Column(sa.Boolean, nullable=False, server_default="false")
    
    # Relationships
    owner = relationship("UserDB", lazy="joined")
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    role_nodes = relationship("RoleNode", back_populates="project", cascade="all, delete-orphan")
    fillout_submissions = relationship("FilloutSubmission", back_populates="project", cascade="all, delete-orphan")
    fillout_data = relationship("FilloutData", back_populates="project", cascade="all, delete")
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "project_name": self.project_name,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner_id": str(self.owner_id),
            "allow_guests": self.allow_guests
        }


class ProjectMember(Base):
    """
    ProjectMember model for storing user-project associations.
    Tracks which users have access to which projects and their role within the project.
    """
    __tablename__ = "project_members"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False, server_default="member")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="members")
    
    # Ensure a user can only be added to a project once
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_members_project_user"),
    )
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": str(self.id),
            "project_id": str(self.project_id),
            "user_id": str(self.user_id),
            "role": self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @classmethod
    def get_user_projects(cls, db, user_id):
        """Get all projects that a user is a member of"""
        return db.query(cls.project).filter(cls.user_id == user_id).all()

    @classmethod
    def is_member(cls, db, project_id, user_id):
        """Check if a user is a member of a project"""
        return db.query(cls).filter(
            cls.project_id == project_id,
            cls.user_id == user_id
        ).first() is not None 