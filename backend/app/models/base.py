from sqlalchemy import Column, String, text, BigInteger, ForeignKey, Enum as SQLEnum, Integer, DateTime, UniqueConstraint, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum
from app.database import Base, SessionLocal
from datetime import datetime
from uuid import uuid4
import secrets
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm.session import object_session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import event

class AuthProvider(str, enum.Enum):
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    GOOGLE = "google"
    EMAIL = "email"
    # Add more providers as needed

def generate_referral_code():
    """Generate a unique referral code"""
    return secrets.token_urlsafe(8)[:11]

# SQLAlchemy Models
class UserDB(Base):
    """Database model for users"""
    __tablename__ = "users"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=True)
    location = Column(String, nullable=True)
    workplace = Column(String, nullable=True)
    role = Column(String, nullable=True)
    birth_date = Column(String, nullable=True)
    goals = Column(String, nullable=True)
    education = Column(String, nullable=True)
    phone_number = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    referral_code = Column(String, unique=True, nullable=False)
    referral_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    willing_to_contribute = Column(Boolean, nullable=True)

    # Relationships
    auth_users = relationship("AuthUser", back_populates="user", cascade="all, delete-orphan")
    user_roles = relationship("UserRoleDB", back_populates="user")
    fillout_submissions = relationship("FilloutSubmission", back_populates="user")
    fillout_data = relationship("FilloutData", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    referrer = relationship("UserDB", remote_side=[uuid], backref="referrals")
    credits = relationship("Credits", back_populates="user", uselist=False, cascade="all, delete-orphan")

# Move event listener outside the class
@event.listens_for(UserDB, 'before_insert')
def set_referral_code(mapper, connection, target):
    """Set unique referral code before insert"""
    if not target.referral_code:
        session = SessionLocal()
        try:
            max_attempts = 100
            for attempt in range(max_attempts):
                code = generate_referral_code()
                exists = session.query(UserDB).filter(
                    UserDB.referral_code == code
                ).first() is not None
                
                if not exists:
                    target.referral_code = code
                    return
                
            raise SQLAlchemyError(f"Failed to generate unique referral code after {max_attempts} attempts")
        finally:
            session.close()

class AuthUser(Base):
    """Base authentication model"""
    __tablename__ = "auth_users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    provider = Column(SQLEnum(AuthProvider, name='auth_provider'), nullable=False)
    user_uuid = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)

    # Relationships
    user = relationship("UserDB", back_populates="auth_users")
    telegram_user = relationship("TelegramUser", back_populates="auth", uselist=False)
    google_user = relationship("GoogleUser", back_populates="auth", uselist=False)
    email_user = relationship("EmailUser", back_populates="auth", uselist=False)
    
class TelegramUser(Base):
    """Telegram user authentication"""
    __tablename__ = "telegram_users"

    auth_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True)
    telegram_id = Column(BigInteger, unique=True, index=True)

    # Relationships
    auth = relationship("AuthUser", back_populates="telegram_user")

class GoogleUser(Base):
    """Google user authentication"""
    __tablename__ = "google_users"

    auth_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True)
    google_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True)

    # Relationships
    auth = relationship("AuthUser", back_populates="google_user")

# Future WhatsApp implementation example:
# class WhatsAppUser(AuthUser):
#     __tablename__ = "whatsapp_users"
#     auth_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True)
#     whatsapp_id = Column(String, unique=True, nullable=False)
#     __mapper_args__ = {
#         'polymorphic_identity': AuthProvider.WHATSAPP,
#     }

class UserRoleDB(Base):
    """Database model for user-role associations"""
    __tablename__ = "user_roles"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.uuid"))
    role = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("UserDB", back_populates="user_roles")

class InvitationDB(Base):
    __tablename__ = "invitations"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    workplace = Column(String, nullable=False)
    role = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    goals = Column(String, nullable=False)
    education = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    referral = Column(UUID(as_uuid=True), ForeignKey('users.uuid'))
    status = Column(String, nullable=False)  # pending, used
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

class EmailUser(Base):
    """Email user authentication"""
    __tablename__ = "email_users"

    auth_id = Column(UUID(as_uuid=True), ForeignKey('auth_users.id', ondelete='CASCADE'), primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)

    # Relationships
    auth = relationship("AuthUser", back_populates="email_user")

class WaitingListDB(Base):
    """Database model for users in waiting list"""
    __tablename__ = "waiting_list"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uuid', ondelete='CASCADE'), nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    approved_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("UserDB", backref="waiting_entry")
