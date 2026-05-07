from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from ..database import get_db
from ..models.base import UserDB, AuthUser, AuthProvider, UserRoleDB, EmailUser
from ..models.payment import Payment
from ..schemas.users import User, ProfileUpdate, UserProfile
from ..schemas.roles import RoleCreate
from ..routers.auth import get_token, verify_token
from pydantic import BaseModel
from PIL import Image
from io import BytesIO
import traceback
import os
import shutil
from uuid import uuid4, UUID
from ..core.constants import AVATARS_DIR, AVATAR_SIZE, AVATAR_MAX_SIZE, ALLOWED_AVATAR_TYPES
from datetime import datetime
import logging
from app.services import credits as credits_service

router = APIRouter()
logger = logging.getLogger(__name__)

# Ensure avatar directory exists
os.makedirs(AVATARS_DIR, exist_ok=True)

class UserData(BaseModel):
    """Input model for user creation"""
    name: str
    location: str
    workplace: str
    birth_date: str
    goals: str
    education: str
    referral: Optional[str] = None
    phone_number: str
    telegram_id: Optional[int] = None  # This will be provider-specific in the future

class RoleResponse(BaseModel):
    id: UUID
    name: str
    label: str

class UserRoleResponse(BaseModel):
    id: int
    role: RoleResponse
    created_at: datetime

class UserResponse(BaseModel):
    uuid: UUID
    email: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    workplace: Optional[str] = None
    birth_date: Optional[str] = None
    goals: Optional[str] = None
    education: Optional[str] = None
    phone_number: Optional[str] = None
    avatar_url: Optional[str] = None
    referral_code: Optional[str] = None
    created_at: Optional[datetime] = None
    credits: Optional[int] = 0
    
    class Config:
        from_attributes = True

class PaymentStatus(BaseModel):
    status: str
    email: str
    payment_id: Optional[str] = None
    total_amount: Optional[float] = None
    currency: Optional[str] = None

@router.post("")
async def create_user(user_data: UserData, db: Session = Depends(get_db)):
    """Create new user or update existing user's data"""
    
    logger.info(f"Processing user creation request with telegram_id: {user_data.telegram_id}")
    
    # Resolve referral code to user UUID if provided
    referral_uuid = None
    if user_data.referral:
        logger.info(f"Attempting to resolve referral code: {user_data.referral}")
        referral_user = db.query(UserDB).filter(
            UserDB.referral_code == user_data.referral
        ).first()
        if referral_user:
            referral_uuid = referral_user.uuid
            logger.info(f"Resolved referral code {user_data.referral} to user UUID: {referral_uuid}")
        else:
            logger.warning(f"Invalid referral code provided: {user_data.referral}")
            raise HTTPException(status_code=400, detail="Invalid referral code")
    
    try:
        if user_data.telegram_id:
            # Check if user with this telegram ID already exists
            logger.info("Checking for existing telegram user")
            telegram_user = db.query(TelegramUser).join(AuthUser).filter(
                TelegramUser.telegram_id == user_data.telegram_id
            ).first()
            
            if telegram_user:
                logger.info(f"Found existing telegram user with auth_id: {telegram_user.auth_id}")
                print(f"Found existing telegram user with auth_id: {telegram_user.auth_id}")
                # Update existing user's data
                user = telegram_user.auth.user
                logger.info(f"Updating existing user with UUID: {user.uuid}")
                print(f"Updating existing user with UUID: {user.uuid}")
                
                user.name = user_data.name
                user.location = user_data.location
                user.workplace = user_data.workplace
                user.birth_date = user_data.birth_date
                user.goals = user_data.goals
                user.education = user_data.education
                user.referral_id = referral_uuid
                user.phone_number = user_data.phone_number
                
                try:
                    db.commit()
                    logger.info(f"Successfully updated user {user.uuid}")
                    print(f"Successfully updated user {user.uuid}")
                    db.refresh(user)
                    return {"uuid": str(user.uuid), "status": "existing"}
                except Exception as e:
                    logger.error(f"Error updating existing user: {e}")

                    db.rollback()
                    raise HTTPException(status_code=500, detail="Error updating user")
        
        # Create new user
        logger.info("Creating new user")
        user = UserDB(
            name=user_data.name,
            location=user_data.location,
            workplace=user_data.workplace,
            birth_date=user_data.birth_date,
            goals=user_data.goals,
            education=user_data.education,
            referral_id=referral_uuid,
            phone_number=user_data.phone_number
        )
        db.add(user)
        db.flush()  # Flush to get the UUID
        logger.info(f"Created user with UUID: {user.uuid}")
        
        # Create auth user
        logger.info("Creating auth user")
        print("Creating auth user")
        auth_user = AuthUser(
            user_uuid=user.uuid,
            provider=AuthProvider.TELEGRAM
        )
        db.add(auth_user)
        db.flush()
        logger.info(f"Created auth user with ID: {auth_user.id}")
        print(f"Created auth user with ID: {auth_user.id}")
        
        # Create telegram user
        logger.info("Creating telegram user")
        telegram_user = TelegramUser(
            auth_id=auth_user.id,
            telegram_id=user_data.telegram_id
        )
        db.add(telegram_user)
        logger.info("Added telegram user to session")
        print("Added telegram user to session")
        
        try:
            db.commit()
            logger.info("Successfully committed all changes to database")
            db.refresh(user)
            return {"uuid": str(user.uuid), "status": "success"}
        except Exception as e:
            logger.error(f"Error during final commit: {e}")
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

async def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    """Verify token and return current user data"""
    try:
        payload = verify_token(token)
        # payload["user_id"] is now a string, but UUID comparison will work
        user = db.query(UserDB).filter(UserDB.uuid == payload["user_id"]).first()
        if not user:
            logger.warning("User not found for token payload: %s", payload)
            raise HTTPException(status_code=404, detail="User not found")                

        return user
    except Exception as e:
        logger.error("Authentication error: %s", str(e))
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )


@router.get("/search", response_model=List[UserResponse])
async def search_users(
    email: str = Query(..., description="Email to search for"),
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Search for users by email"""
    # Join with EmailUser to search by email and retrieve email in a single query
    results = db.query(
        UserDB, 
        EmailUser.email
    ).join(
        AuthUser, AuthUser.user_uuid == UserDB.uuid
    ).join(
        EmailUser, EmailUser.auth_id == AuthUser.id
    ).filter(
        EmailUser.email.ilike(f"%{email}%")
    ).limit(10).all()
    
    return [
        UserResponse(
            uuid=user.uuid,
            email=email,
            name=user.name,
            created_at=user.created_at.isoformat() if user.created_at else None
        ) for user, email in results
    ]

@router.get("/{uuid}", response_model=UserResponse)
async def get_user(uuid: str, db: Session = Depends(get_db)):
    """Get a user by UUID"""
    user = db.query(UserDB).filter(UserDB.uuid == uuid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_credits = user.credits.credits

    return UserResponse(
        uuid=str(user.uuid),
        name=user.name,
        location=user.location,
        workplace=user.workplace,
        birth_date=user.birth_date,
        goals=user.goals,
        education=user.education,
        phone_number=user.phone_number,
        avatar_url=user.avatar_url,
        referral_code=user.referral_code,
        created_at=user.created_at,
        credits=user_credits.credits if user_credits else 0
    )

@router.get("/verify-referral/{referral_code}")
async def verify_referral(
    referral_code: str,
    db: Session = Depends(get_db)
):
    """Verify referral code and return referrer's name"""
    logger.info(f"Verifying referral code: {referral_code}")
    
    try:
        referrer = db.query(UserDB).filter(
            UserDB.referral_code == referral_code
        ).first()
        
        if not referrer:
            logger.warning(f"Invalid referral code: {referral_code}")
            raise HTTPException(status_code=404, detail="Invalid referral code")
        
        logger.info(f"Found referrer: {referrer.name} (UUID: {referrer.uuid})")
        return {
            "name": referrer.name,
            "uuid": str(referrer.uuid)
        }
        
    except Exception as e:
        logger.error(f"Error verifying referral code: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Error verifying referral code"
        )


@router.put("/profile", response_model=Dict[str, Any])
async def update_profile(
    data: ProfileUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Update user profile"""
    try:
        # Update user fields
        current_user.name = data.name
        current_user.location = data.location
        current_user.workplace = data.workplace
        current_user.role = data.role
        current_user.birth_date = data.birth_date
        current_user.goals = data.goals
        current_user.education = data.education
        current_user.phone_number = data.phone_number

        # Explicitly mark as modified
        db.add(current_user)
        
        try:
            db.commit()
            logger.info("Profile updated successfully")
        except Exception as commit_error:
            logger.error("Error committing changes: %s", str(commit_error))
            db.rollback()
            raise

        user_credits = current_user.credits

        user = User(
            uuid=str(current_user.uuid),
            name=current_user.name,
            location=current_user.location,
            workplace=current_user.workplace,
            role=current_user.role,
            birth_date=current_user.birth_date,
            goals=current_user.goals,
            education=current_user.education,
            phone_number=current_user.phone_number,
            referral_code=current_user.referral_code,
            referral=str(current_user.referral_id) if current_user.referral_id else None,
            avatar_url=current_user.avatar_url,
            credits=user_credits.credits if user_credits else 0
        )

        return {
            "success": True,
            "user": user
        }

    except Exception as e:
        db.rollback()
        logger.error("Profile update error: %s", str(e))
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Error updating profile")

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: UserDB = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload user avatar"""
    try:
        # Validate file size
        contents = await file.read()
        if len(contents) > AVATAR_MAX_SIZE:
            raise HTTPException(status_code=400, detail="File too large")

        # Validate file type
        if file.content_type not in ALLOWED_AVATAR_TYPES:
            raise HTTPException(status_code=400, detail="Invalid file type")

        # Process image
        image = Image.open(BytesIO(contents))
        image = image.convert('RGB')
        image.thumbnail(AVATAR_SIZE)

        # Generate filename using user UUID
        filename = f"{current_user.uuid}.jpg"
        filepath = os.path.join(AVATARS_DIR, filename)

        # Save processed image
        image.save(filepath, "JPEG", quality=85)

        # Update database - get fresh instance from current session
        user = db.query(UserDB).filter(UserDB.uuid == current_user.uuid).first()
        avatar_url = f"/avatars/{filename}"
        user.avatar_url = avatar_url
        db.commit()

        return {"success": True, "avatar_url": avatar_url}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Avatar upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Error uploading avatar")


@router.get("/payment-status", response_model=PaymentStatus)
async def get_payment_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current user's payment status"""
    # Get the most recent payment for the user
    payment = db.query(Payment).filter(
        Payment.user_id == UUID(current_user.uuid)
    ).order_by(Payment.created_at.desc()).first()
    
    if not payment:
        # If no payment found, return default status
        return PaymentStatus(
            status="none",
            email=""
        )
    
    return PaymentStatus(
        status=payment.status,
        email=payment.email,
        payment_id=payment.payment_id,
        total_amount=payment.total_amount,
        currency=payment.currency
    ) 