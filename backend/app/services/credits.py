from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.models.credits import Credits
from app.models.base import UserDB
import logging

logger = logging.getLogger(__name__)

def get_user_credits(db: Session, user_uuid: str) -> Credits:
    """Get credits for a user"""
    credits = db.query(Credits).filter(Credits.user_uuid == user_uuid).first()
    
    # If the user doesn't have a credits record yet, create one
    if not credits:
        credits = create_user_credits(db, user_uuid)
        
    return credits

def create_user_credits(db: Session, user_uuid: str, initial_credits: int = 0) -> Credits:
    """Create a credits record for a user"""
    try:
        # Check if the user exists
        user = db.query(UserDB).filter(UserDB.uuid == user_uuid).first()
        if not user:
            logger.error(f"User with UUID {user_uuid} not found")
            return None
            
        # Create credits record
        credits = Credits(
            user_uuid=user_uuid,
            credits=initial_credits
        )
        
        db.add(credits)
        db.commit()
        db.refresh(credits)
        
        logger.info(f"Created credits record for user {user_uuid} with {initial_credits} credits")
        return credits
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error creating credits record: {str(e)}")
        return None

def update_user_credits(db: Session, user_uuid: str, amount: int) -> Credits:
    """Update credits for a user - can be positive to add or negative to subtract"""
    try:
        credits = get_user_credits(db, user_uuid)
        
        if not credits:
            logger.error(f"No credits record found for user {user_uuid}")
            return None
        
        # Update credits amount (can be positive or negative)
        credits.credits += amount
        
        # Ensure credits don't go below zero
        if credits.credits < 0:
            credits.credits = 0
            
        db.commit()
        db.refresh(credits)
        
        logger.info(f"Updated credits for user {user_uuid} by {amount} to {credits.credits}")
        return credits
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error updating credits: {str(e)}")
        return None

def set_user_credits(db: Session, user_uuid: str, amount: int) -> Credits:
    """Set credits for a user to a specific amount"""
    try:
        credits = get_user_credits(db, user_uuid)
        
        if not credits:
            logger.error(f"No credits record found for user {user_uuid}")
            return None
        
        # Set credits to specific amount
        credits.credits = max(0, amount)  # Ensure it's not negative
            
        db.commit()
        db.refresh(credits)
        
        logger.info(f"Set credits for user {user_uuid} to {credits.credits}")
        return credits
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error setting credits: {str(e)}")
        return None 