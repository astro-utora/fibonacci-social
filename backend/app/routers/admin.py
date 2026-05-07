from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any, Optional
from ..database import get_db
from .auth import is_admin
from app.models import UserDB, UserRoleDB, FilloutSubmission, RoleNode
from app.schemas.user_forms import UserFormEntry, PaginatedUserFormResponse
from app.schemas.form_validation import FormValidationRequest
from app.schemas.admin import AdminSetting as AdminSettingSchema, AdminSettingUpdate
from app.models import AdminSetting
from app.routers.users import get_current_user
import uuid
from datetime import datetime

router = APIRouter()

DEFAULT_FILLOUT_ONBOARDING_ID = "clm2xb2e700cml708htlwd8co"

def validate_admin_access(current_user: UserDB, db: Session):
    """Ensure current user has admin role"""
    if not is_admin(current_user, db):
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


@router.get("/settings", response_model=List[AdminSettingSchema])
async def get_admin_settings(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Get all admin settings"""
    # Check admin access
    validate_admin_access(current_user, db)
    
    settings = db.query(AdminSetting).all()
    return settings

@router.get("/settings/{key}", response_model=AdminSettingSchema)
async def get_admin_setting(
    key: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Get a specific admin setting by key"""
    # Check admin access
    validate_admin_access(current_user, db)
    
    setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting with key '{key}' not found")
    
    return setting

@router.put("/settings/{key}", response_model=AdminSettingSchema)
async def update_admin_setting(
    key: str,
    setting_update: AdminSettingUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """Update a specific admin setting by key"""
    # Check admin access
    validate_admin_access(current_user, db)
    
    setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail=f"Setting with key '{key}' not found")
    
    # Update setting
    setting.value = setting_update.value
    if setting_update.description is not None:
        setting.description = setting_update.description
    
    db.commit()
    db.refresh(setting)
    
    return setting

# Public endpoint to get filloutOnboardingId
@router.get("/settings/public/filloutOnboardingId")
async def get_fillout_onboarding_id(
    db: Session = Depends(get_db)
):
    """Get the filloutOnboardingId setting (public endpoint)"""
    setting = db.query(AdminSetting).filter(AdminSetting.key == "filloutOnboardingId").first()
    if not setting:
        # Return default value if not found
        return {"value": DEFAULT_FILLOUT_ONBOARDING_ID}
    
    return {"value": setting.value}

@router.get("/user-forms", response_model=PaginatedUserFormResponse)
async def get_user_forms(
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Get all user form submissions for admin monitoring.
    
    Returns a list of user form entries with:
    - User UUID
    - User name
    - Fillout ID
    - Start date
    - Complete date (if completed)
    - Request date (if validation was requested)
    - Validation date (if validated)
    
    Only shows submissions that aren't associated with any project (project_id is NULL).
    Supports pagination.
    """
    # Validate admin access (will raise HTTPException if not admin)
    validate_admin_access(current_user, db)
    
    # Query to join users, roles, and form submissions
    query = (
        db.query(
            UserDB.uuid.label("user_id"),
            UserDB.name.label("user_name"),
            RoleNode.role.label("role_name"),
            FilloutSubmission.id.label("id"),
            FilloutSubmission.fillout_id.label("fillout_id"),
            FilloutSubmission.started_at.label("start_date"),
            FilloutSubmission.submitted_at.label("complete_date"),
            FilloutSubmission.requested_at.label("requested_date"),
            FilloutSubmission.validated_at.label("validated_date"),
        )
        .join(FilloutSubmission, FilloutSubmission.user_id == UserDB.uuid)
        .join(RoleNode, FilloutSubmission.fillout_id == RoleNode.fillout_id)
        # Only include submissions with NULL project_id
        .filter(FilloutSubmission.project_id.is_(None))
    )
    
    # Get total count for pagination metadata
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    results = query.order_by(FilloutSubmission.started_at.desc()).offset(offset).limit(page_size).all()
    
    # Transform query results to response schema
    user_form_items = [
        UserFormEntry(
            id=str(row.id),
            userId=str(row.user_id),
            userName=row.user_name,
            role=row.role_name,
            filloutId=row.fillout_id,
            startDate=row.start_date.isoformat() if row.start_date else None,
            completeDate=row.complete_date.isoformat() if row.complete_date else None,
            requestedDate=row.requested_date.isoformat() if row.requested_date else None,
            validatedDate=row.validated_date.isoformat() if row.validated_date else None,
        )
        for row in results
    ]
    
    # Return paginated response
    return {
        "items": user_form_items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size
        }
    }

@router.post("/validate-form", response_model=UserFormEntry)
async def validate_form(
    validation: FormValidationRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Validate a form submission by setting the validated_at timestamp.
    
    Requires admin access.
    """
    # Validate admin access (will raise HTTPException if not admin)
    validate_admin_access(current_user, db)
    
    # Find the form submission
    submission_query = db.query(FilloutSubmission).filter(
        FilloutSubmission.fillout_id == validation.filloutId,
        FilloutSubmission.user_id == uuid.UUID(validation.userId)
    )
    
    # Add project filter if provided
    if validation.projectId:
        submission_query = submission_query.filter(
            FilloutSubmission.project_id == uuid.UUID(validation.projectId)
        )
    
    submission = submission_query.first()
    
    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Form submission not found"
        )
    
    if not submission.requested_at:
        raise HTTPException(
            status_code=400,
            detail="Form validation not requested yet"
        )
    
    # Set validated_at timestamp
    submission.validated_at = datetime.utcnow()
    db.commit()
    db.refresh(submission)
    
    # Get related user and role for response
    user = db.query(UserDB).filter(UserDB.uuid == submission.user_id).first()
    role = db.query(RoleNode).filter(RoleNode.fillout_id == submission.fillout_id).first()
    
    return UserFormEntry(
        id=str(submission.id),
        userId=str(user.uuid),
        userName=user.name,
        role=role.role if role else "Unknown",
        filloutId=submission.fillout_id,
        startDate=submission.started_at.isoformat() if submission.started_at else None,
        completeDate=submission.submitted_at.isoformat() if submission.submitted_at else None,
        requestedDate=submission.requested_at.isoformat() if submission.requested_at else None,
        validatedDate=submission.validated_at.isoformat() if submission.validated_at else None,
    )

@router.post("/reject-validation", response_model=UserFormEntry)
async def reject_validation(
    validation: FormValidationRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user)
):
    """
    Reject a form validation request by clearing the requested_at timestamp.
    
    Requires admin access.
    """
    # Validate admin access (will raise HTTPException if not admin)
    validate_admin_access(current_user, db)
    
    # Find the form submission
    submission_query = db.query(FilloutSubmission).filter(
        FilloutSubmission.fillout_id == validation.filloutId,
        FilloutSubmission.user_id == uuid.UUID(validation.userId)
    )
    
    # Add project filter if provided
    if validation.projectId:
        submission_query = submission_query.filter(
            FilloutSubmission.project_id == uuid.UUID(validation.projectId)
        )
    
    submission = submission_query.first()
    
    if not submission:
        raise HTTPException(
            status_code=404,
            detail="Form submission not found"
        )
    
    if not submission.requested_at:
        raise HTTPException(
            status_code=400,
            detail="Form validation not requested yet"
        )
    
    # Clear requested_at timestamp
    submission.requested_at = None
    db.commit()
    db.refresh(submission)
    
    # Get related user and role for response
    user = db.query(UserDB).filter(UserDB.uuid == submission.user_id).first()
    role = db.query(RoleNode).filter(RoleNode.fillout_id == submission.fillout_id).first()
    
    return UserFormEntry(
        id=str(submission.id),
        userId=str(user.uuid),
        userName=user.name,
        role=role.role if role else "Unknown",
        filloutId=submission.fillout_id,
        startDate=submission.started_at.isoformat() if submission.started_at else None,
        completeDate=submission.submitted_at.isoformat() if submission.submitted_at else None,
        requestedDate=submission.requested_at.isoformat() if submission.requested_at else None,
        validatedDate=submission.validated_at.isoformat() if submission.validated_at else None,
    ) 