from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Dict, Optional
from uuid import UUID
from ..database import get_db
from ..models import (
    UserDB, 
    TelegramUser, 
    InvitationDB, 
    AuthUser, 
    GoogleUser, 
    EmailUser, 
    AuthProvider, 
    UserRoleDB,
    WaitingListDB
)
from ..models.payment import Payment
from ..models.project import Project, ProjectMember
from ..schemas.auth import (
    LoginResponse,
    EmailRegister,
    EmailLogin,
    InvitationCreate,
    InvitationResponse
)
from ..schemas.users import User
import hashlib
import hmac
import os
import jwt
from jwt.exceptions import InvalidTokenError, DecodeError, ExpiredSignatureError
from datetime import datetime, timedelta
import logging
from sqlalchemy import and_
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests
from ..utils.password import hash_password, verify_password
from ..core.email import send_verification_email
import secrets

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key")  # Use environment variable in production
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=30)

class TelegramAuth(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    photo_url: str | None = None
    auth_date: int
    hash: str
    invitation_id: Optional[UUID] = None

class GoogleAuth(BaseModel):
    token: str
    invitation_id: Optional[UUID] = None

def verify_telegram_data(data: Dict, hash: str) -> bool:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not BOT_TOKEN:
        raise HTTPException(status_code=500, detail="Bot token not configured")

    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(
        data.items(),
        key=lambda x: x[0]
    ))
    
    calculated_hash = hmac.new(
        secret_key,
        data_check_string.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hash == calculated_hash


def generate_token(user: UserDB) -> str:
    """Generate JWT token for user"""
    payload = {
        "user_id": str(user.uuid),
        "exp": datetime.utcnow() + JWT_EXPIRATION_DELTA
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> Dict:
    """Verify JWT token and return payload"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token has expired")
        raise HTTPException(status_code=401, detail="Token has expired")
    except (jwt.InvalidTokenError, jwt.DecodeError) as e:
        logger.error("Invalid token: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        logger.error("Unexpected token error: %s", str(e))
        raise HTTPException(status_code=401, detail="Invalid authentication")

async def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Get token from Authorization header"""
    return credentials.credentials

def create_user_response(user: UserDB, token: str, is_admin: bool) -> LoginResponse:
    """Create standardized login response from UserDB"""
    # Get database session
    db = next(get_db())
    
    # Get payment status
    payment = db.query(Payment).filter(
        Payment.user_id == user.uuid
    ).order_by(Payment.created_at.desc()).first()
    
    payment_status = None
    
    if payment:
        payment_status = payment.status
    
    # Get waiting list status
    waiting_entry = db.query(WaitingListDB).filter(
        WaitingListDB.user_id == user.uuid
    ).first()
    
    waiting_list_status = waiting_entry.status if waiting_entry else None
    
    user_response = User(
        uuid=str(user.uuid),
        name=user.name,
        location=user.location,
        workplace=user.workplace,
        birth_date=user.birth_date,
        goals=user.goals,
        education=user.education,
        phone_number=user.phone_number,
        referral_code=user.referral_code,
        avatar_url=user.avatar_url,
        willing_to_contribute=user.willing_to_contribute,
        is_admin=is_admin,
        payment_status=payment_status,
        waiting_list_status=waiting_list_status
    )

    return LoginResponse(
        success=True,
        user=user_response,
        token=token
    )

def is_admin(user: UserDB, db: Session) -> bool:
    """Check if user has admin role"""
    admin_role = db.query(UserRoleDB).filter(
        UserRoleDB.user_id == user.uuid,
        UserRoleDB.role == 'admin'  # Direct check in user_roles table
    ).first()
    
    return admin_role is not None

@router.post("/telegram", response_model=LoginResponse)
async def telegram_login(
    data: TelegramAuth,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Handle Telegram login and return user data"""
    logger.info("Received Telegram auth data: %s", data.dict())

    # Remove hash for verification
    data_dict = data.dict()
    telegram_hash = data_dict.pop('hash')
    invitation_id = data_dict.pop('invitation_id', None)

    try:
        if not verify_telegram_data(data_dict, telegram_hash):
            raise HTTPException(status_code=401, detail="Invalid authentication data")
    except Exception as e:
        logger.error("Verification error: %s", str(e))
        raise HTTPException(status_code=401, detail=str(e))
    db = next(get_db())
    
    # Find existing user
    # Check if user exists by telegram_id
    telegram_user = db.query(TelegramUser).join(AuthUser).filter(
        TelegramUser.telegram_id == data.id
    ).first()

    user = telegram_user.auth.user if telegram_user else None

    # Handle invitation
    if user is None:
        try:
            if invitation_id:
                invitation = get_invitation(db, data.invitation_id)
                # Create user from invitation data
                user = create_user_from_invitation(db, invitation)
            else:
                raise HTTPException(status_code=400, detail="Invitation required for registration")

            # Create AuthUser
            auth_user = AuthUser(
                provider="telegram",
                user_uuid=user.uuid
            )
            db.add(auth_user)
            db.flush()

            # Create TelegramUser
            telegram_user = TelegramUser(
                auth_id=auth_user.id,
                telegram_id=data.id
            )
            db.add(telegram_user)

            # Mark invitation as used
            invitation.status = "used"

            db.commit()
            logger.info("Created new user with Telegram auth")

        except Exception as e:
            db.rollback()
            logger.error("Error creating user: %s", str(e))
            raise HTTPException(status_code=500, detail="Error creating user account")
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    token = generate_token(user)
    
    return create_user_response(user, token, is_admin(user, db))

def get_invitation(db: Session, invitation_id: UUID) -> InvitationDB:
    invitation = db.query(InvitationDB).filter(
        and_(
            InvitationDB.id == invitation_id,
            InvitationDB.status == "pending"
        )
    ).first()
        
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or already used")
    
    return invitation

async def create_user_from_invitation(db: Session, invitation: InvitationDB) -> UserDB:
    """Create new user from invitation data"""
    user = UserDB(
        name=invitation.name,
        location=invitation.location,
        workplace=invitation.workplace,
        birth_date=invitation.birth_date,
        goals=invitation.goals,
        education=invitation.education,
        phone_number=invitation.phone_number,
        referral_id=invitation.referral
    )
    db.add(user)
    db.flush()
    return user

@router.post("/google", response_model=LoginResponse)
async def google_login(
    data: GoogleAuth,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Handle Google login and return user data"""
    try:
        # Verify Google token
        GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(
            data.token, requests.Request(), GOOGLE_CLIENT_ID)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        google_id = idinfo['sub']
        email = idinfo['email']
        
        # Find existing user
        google_user = db.query(GoogleUser).join(AuthUser).filter(
            GoogleUser.google_id == google_id
        ).first()

        user = google_user.auth.user if google_user else None

        # Handle new user registration
        if user is None:
            try:
                if data.invitation_id:
                    # Create user from invitation data
                    invitation = get_invitation(db, data.invitation_id)
                    user = create_user_from_invitation(db, invitation)
                else:
                    invitation = None
                    # Create user from Google data
                    user = UserDB(
                        name=idinfo.get('name', ''),
                        location='',
                        role='',
                        workplace='',
                        birth_date='',
                        goals='',
                        education='',
                        phone_number=''
                    )
                    db.add(user)
                    db.flush()

                # Create AuthUser
                auth_user = AuthUser(
                    provider="google",
                    user_uuid=user.uuid
                )
                db.add(auth_user)
                db.flush()

                # Create GoogleUser
                google_user = GoogleUser(
                    auth_id=auth_user.id,
                    google_id=google_id,
                    email=email
                )
                db.add(google_user)

                if invitation:
                    # Mark invitation as used
                    invitation.status = "used"
                
                db.commit()
                logger.info("Created new user with Google auth")

            except Exception as e:
                db.rollback()
                logger.error("Error creating user: %s", str(e))
                raise HTTPException(status_code=500, detail="Error creating user account")

        # Generate token and prepare response
        token = generate_token(user)
        
        return create_user_response(user, token, is_admin(user, db))

    except ValueError as e:
        logger.error("Google auth error: %s", str(e))
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error("Unexpected error in google_login: %s", str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/me")
async def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    """Verify token and return current user data"""
    try:
        payload = verify_token(token)
        # payload["user_id"] is now a string, but UUID comparison will work
        user = db.query(UserDB).filter(UserDB.uuid == payload["user_id"]).first()
        if not user:
            logger.warning("User not found for token payload: %s", payload)
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get payment status
        payment = db.query(Payment).filter(
            Payment.user_id == user.uuid
        ).order_by(Payment.created_at.desc()).first()
        
        payment_status = None
        
        if payment:
            payment_status = payment.status
        
        # Get user credits
        user_credits = 0
        if user.credits:
            user_credits = user.credits.credits
        
        # Get waiting list status
        waiting_entry = db.query(WaitingListDB).filter(
            WaitingListDB.user_id == user.uuid
        ).first()
        
        waiting_list_status = waiting_entry.status if waiting_entry else None
        
        user_data = User(
            uuid=str(user.uuid),
            name=user.name,
            location=user.location,
            workplace=user.workplace,
            role=user.role,
            birth_date=user.birth_date,
            goals=user.goals,
            education=user.education,
            phone_number=user.phone_number,
            referral_code=user.referral_code,
            avatar_url=user.avatar_url,
            willing_to_contribute=user.willing_to_contribute,
            is_admin=is_admin(user, db),
            payment_status=payment_status,
            credits=user_credits,
            waiting_list_status=waiting_list_status
        )

        return user_data
    except Exception as e:
        logger.error("Authentication error: %s", str(e))
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

@router.post("/register", response_model=LoginResponse)
async def register(
    data: EmailRegister,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Handle email registration"""
    try:
        # Check if email already exists
        existing_user = db.query(EmailUser).filter(
            EmailUser.email == data.email
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Handle invitation if provided
        if data.invitation_id:
            invitation = get_invitation(db, data.invitation_id)
            user = create_user_from_invitation(db, invitation)
        else:
            invitation = None
            referral_uuid = None
            if data.referral:
                referral_user = db.query(UserDB).filter(
                    UserDB.referral_code == data.referral
                ).first()
                if referral_user:
                    referral_uuid = referral_user.uuid
                else:
                    logger.warning("Referral user not found")

            # Create minimal user record
            user = UserDB(
                name='',
                location='',
                workplace='',
                birth_date='',
                goals='',
                education='',
                phone_number='',
                referral_id=referral_uuid
            )
            db.add(user)
            db.flush()

        # Create AuthUser
        auth_user = AuthUser(
            provider=AuthProvider.EMAIL,
            user_uuid=user.uuid
        )
        db.add(auth_user)
        db.flush()

        # Generate verification token
        verification_token = secrets.token_urlsafe(32)
        
        # Create EmailUser with verification token
        email_user = EmailUser(
            auth_id=auth_user.id,
            email=data.email,
            password_hash=hash_password(data.password),
            verification_token=verification_token,
            is_verified=False
        )
        db.add(email_user)

        if invitation:
            invitation.status = "used"
        else:
            # If user was not invited, add them to the waiting list
            waiting_entry = WaitingListDB(
                user_id=user.uuid,
                status="pending"
            )
            db.add(waiting_entry)

        db.commit()

        # Send verification email
        # await send_verification_email(data.email, verification_token)

        # Generate token and prepare response
        token = generate_token(user)
        return create_user_response(user, token, is_admin(user, db))

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error("Registration error: %s", str(e))
        raise HTTPException(status_code=500, detail="Error during registration")

@router.post("/login", response_model=LoginResponse)
async def login(
    data: EmailLogin,
    db: Session = Depends(get_db)
) -> LoginResponse:
    """Handle email login"""
    try:
        # Find user by email
        email_user = db.query(EmailUser).join(AuthUser).filter(
            EmailUser.email == data.email
        ).first()

        if not email_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(data.password, email_user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        user = email_user.auth.user
        token = generate_token(user)
        return create_user_response(user, token, is_admin(user, db))

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error: %s", str(e))
        raise HTTPException(status_code=500, detail="Error during login")

@router.get("/verify-email/{token}")
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user's email address"""
    try:
        email_user = db.query(EmailUser).filter(
            EmailUser.verification_token == token,
            EmailUser.is_verified == False
        ).first()
        
        if not email_user:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification token"
            )
        
        email_user.is_verified = True
        email_user.verification_token = None
        db.commit()
        
        return {"success": True, "message": "Email verified successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error("Email verification error: %s", str(e))
        raise HTTPException(
            status_code=500,
            detail="Error verifying email"
        )
