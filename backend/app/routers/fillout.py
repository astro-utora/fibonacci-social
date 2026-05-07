from fastapi import APIRouter, Depends, HTTPException, Request, Body
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid
from typing import List, Optional, Dict, Any, Union
from app.database import get_db
from ..models import FilloutSubmission, FilloutData, UserDB, Project, ProjectMember
from app.schemas.users import User
from app.routers.users import get_current_user
from pydantic import BaseModel, Field
import logging
import json
import hmac
import hashlib
import base64
from app.services import credits as credits_service
import traceback
from sqlalchemy.sql import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

router = APIRouter()

class FilloutIdData(BaseModel):
    filloutId: str
    project_id: Optional[str] = None

# Pydantic models for Fillout webhook data
class FilloutQuestion(BaseModel):
    id: str
    name: str
    type: str
    value: Optional[Any] = None

class FilloutUrlParameter(BaseModel):
    id: str
    name: str
    value: Optional[str] = None

class FilloutPaymentValue(BaseModel):
    email: Optional[str] = None
    status: Optional[str] = None
    paymentId: Optional[str] = None
    totalAmount: Optional[float] = None
    currency: Optional[str] = None

class FilloutPayment(BaseModel):
    id: str
    name: str
    value: Optional[FilloutPaymentValue] = None

class FilloutSubmissionData(BaseModel):
    submissionId: str = ""
    submissionTime: str
    lastUpdatedAt: str
    questions: List[FilloutQuestion]
    urlParameters: List[FilloutUrlParameter] = []
    calculations: List[Dict[str, Any]] = []
    quiz: Dict[str, Any] = {}
    documents: List[Dict[str, Any]] = []
    scheduling: List[Dict[str, Any]] = []
    payments: List[FilloutPayment] = []

class FilloutWebhookPayload(BaseModel):
    formId: str
    formName: str
    submission: FilloutSubmissionData

class WebhookResponse(BaseModel):
    success: bool
    message: str = ""
    error: Optional[str] = None

def validate_project_access(db: Session, project_id: str, current_user: UserDB):
    """
    Validate if the current user has access to the project
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Check if user is a member of the project
    is_member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.uuid
    ).first()
    
    if not is_member and project.owner_id != current_user.uuid:
        raise HTTPException(status_code=403, detail="Access denied to this project")

@router.post("/start")
async def start_fillout(
    fillout_start: FilloutIdData,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Record the start of a fillout form
    """
    fillout_id = fillout_start.filloutId
    project_id = fillout_start.project_id
    
    # Check if there's an existing submission for this user and fillout
    existing_submission = db.query(FilloutSubmission).filter(
        FilloutSubmission.user_id == current_user.uuid,
        FilloutSubmission.fillout_id == fillout_id
    )
    
    # Add project filter if provided
    if project_id:
        validate_project_access(db, project_id, current_user)

        existing_submission = existing_submission.filter(
            FilloutSubmission.project_id == uuid.UUID(project_id)
        )
    
    existing_submission = existing_submission.first()
    
    if existing_submission:
        # Update the existing record - reset status if it was previously completed
        if existing_submission.submitted_at:
            logger.info(f"Resetting previously completed fillout: {fillout_id}")
            existing_submission.submitted_at = None
            existing_submission.requested_at = None
            existing_submission.validated_at = None
        
        db.commit()
        submission_id = existing_submission.id
    else:
        # Create a new fillout submission record
        submission = FilloutSubmission(
            user_id=current_user.uuid,
            fillout_id=fillout_id,
            started_at=datetime.now(timezone.utc)
        )
        
        # Add project association if provided
        if project_id:
            submission.project_id = uuid.UUID(project_id)
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        submission_id = submission.id

    return {"status": "started", "id": str(submission_id)}

@router.post("/complete")
async def complete_fillout(
    fillout_complete: FilloutIdData,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark a fillout as completed
    """
    fillout_id = fillout_complete.filloutId
    project_id = fillout_complete.project_id
    
    # Find existing fillout submission
    query = db.query(FilloutSubmission).filter(
        FilloutSubmission.fillout_id == fillout_id,
        FilloutSubmission.user_id == current_user.uuid
    )
    
    # Add project filter if provided
    if project_id:
        validate_project_access(db, project_id, current_user)
        
        query = query.filter(FilloutSubmission.project_id == uuid.UUID(project_id))
    
    submission = query.first()
    
    if not submission:
        # Create a new record if none exists and mark as completed
        submission = FilloutSubmission(
            user_id=current_user.uuid,
            fillout_id=fillout_id,
            started_at=datetime.now(timezone.utc),
            submitted_at=datetime.now(timezone.utc)
        )
        
        # Add project association if provided
        if project_id:
            submission.project_id = uuid.UUID(project_id)
        
        db.add(submission)
        db.commit()
        db.refresh(submission)
        submission_id = submission.id
    else:
        # Update existing record
        submission.submitted_at = datetime.now(timezone.utc)
        db.commit()
        submission_id = submission.id
    
    return {"status": "completed", "id": str(submission_id)}

def mark_fillout_complete(db: Session, fillout_id: str, user_id: str):
    """
    Mark a fillout submission as completed
    Returns the submission ID if successful, raises HTTPException otherwise
    """
    # Find existing fillout submission
    fillout_submission = db.query(FilloutSubmission).filter(
        FilloutSubmission.fillout_id == fillout_id,
        FilloutSubmission.user_id == user_id,
        FilloutSubmission.submitted_at.is_(None)
    ).first()
    
    if not fillout_submission:
        raise HTTPException(status_code=404, detail="Fillout not found or already completed")
    
    # Update status
    fillout_submission.submitted_at = datetime.now(timezone.utc)
    fillout_submission.requested_at = None
    fillout_submission.validated_at = None
    db.commit()
    
    return fillout_submission.id

@router.get("/submissions")
async def get_user_submissions(
    project_id: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all fillout submissions for the current user
    If project_id is provided, returns only submissions for that project.
    """
    # Check project access if project_id is provided
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
            
        # Check if user is a member of the project
        is_member = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == current_user.uuid
        ).first()
        
        if not is_member and project.owner_id != current_user.uuid:
            raise HTTPException(status_code=403, detail="Access denied to this project")
    
    # Query submissions based on project_id filter
    query = db.query(FilloutSubmission).filter(
        FilloutSubmission.user_id == current_user.uuid,
    )
    
    if project_id is not None:
        query = query.filter(FilloutSubmission.project_id == project_id)
    
    submissions = query.all()
    
    result = []
    for submission in submissions:
        # Determine the status based on timestamps
        status = None
        if submission.validated_at:
            status = 'validated'
        elif submission.requested_at:
            status = 'requested'
        elif submission.submitted_at:
            status = 'completed'
        elif submission.started_at:
            status = 'started'
            
        result.append({
            "id": submission.id,
            "filloutId": submission.fillout_id,
            "submittedAt": submission.submitted_at.isoformat() if submission.submitted_at else None,
            "startedAt": submission.started_at.isoformat() if submission.started_at else None,
            "requestedAt": submission.requested_at.isoformat() if submission.requested_at else None,
            "validatedAt": submission.validated_at.isoformat() if submission.validated_at else None,
            "status": status,
            "projectId": submission.project_id  # Include project_id in the response
        })
    
    return result

@router.post("/role_webhook")
async def role_webhook(
    data: dict,
    db: Session = Depends(get_db)
):
    """Webhook for Fillout form role submissions.
    This receives data from Fillout when a form is completed and updates our system.
    """
    try:
        logger.info(f"Role webhook received: {data}")
        
        form_id = data.get("formId")
        submission = data.get("submission", {})
        submission_id = submission.get("submissionId")
        calculations = submission.get("calculations", [])
        
        # Extract userId from URL parameters if available
        user_id = None
        url_parameters = submission.get("urlParameters", [])
        for param in url_parameters:
            if isinstance(param, dict) and param.get("name") == "userId":
                user_id = param.get("value")
                break
        
        if not form_id or not user_id or not submission_id:
            logger.error("Missing formId, userId or submissionId in webhook data")
            return {"success": False, "error": "Missing required fields"}
        
        try:
            mark_fillout_complete(db, form_id, user_id)
        except HTTPException as e:
            pass
        
        # Process Contribution Score calculation if present
        # Extract Contribution Score from calculations
        credit_score = None
        for calc in calculations:
            if calc.get("name") == "Contribution Score":
                try:
                    credit_score = int(calc.get("value", 0))
                except (ValueError, TypeError):
                    credit_score = 0
                break
        
        # Check if a record already exists for this user and form
        existing_record = db.query(FilloutData).filter(
            FilloutData.user_id == user_id,
            FilloutData.form_id == form_id
        ).first()
        
        if existing_record:
            # Update the existing record
            existing_record.data = submission.get("questions", [])
            existing_record.updated_at = datetime.now(timezone.utc)
            logger.info(f"Updated existing fillout data for user {user_id}, form {form_id}")
        else:
            # Create a new record
            new_fillout_data = FilloutData(
                user_id=user_id,
                form_id=form_id,
                data=submission.get("questions", [])
            )
            db.add(new_fillout_data)
            logger.info(f"Created new fillout data for user {user_id}, form {form_id}")

            # Update user credits if a score was found
            if credit_score is not None:
                logger.info(f"Adding {credit_score} credits to user {user_id} from form submission")
                credits_service.update_user_credits(db, user_id, credit_score)

        db.commit()

        return {"success": True}
    except Exception as e:
        logger.error(f"Error processing role webhook: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        return {"success": False, "error": str(e)}

@router.post("/registration_webhook", response_model=WebhookResponse)
async def registration_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Process registration webhook from Fillout.com
    Updates user profile data and records payment information
    """
    try:
        # Parse the webhook payload using Pydantic
        raw_data = await request.json()
        logger.info(f"Registration webhook received: {raw_data}")
        
        # Validate and parse the data with Pydantic
        payload = FilloutWebhookPayload.parse_obj(raw_data)
        
        # Extract user profile data from questions
        user_data = {}
        
        for question in payload.submission.questions:
            question_name = question.name.lower()
            value = question.value
            
            # Map question fields to user profile fields
            if value is not None:
                if "name" in question_name:
                    user_data["name"] = value
                elif "phone" in question_name:
                    user_data["phone_number"] = value
                elif "email" in question_name:
                    user_data["email"] = value
                elif "location" in question_name:
                    user_data["location"] = value
                elif "education" in question_name:
                    user_data["education"] = value
                elif "goals" in question_name:
                    user_data["goals"] = value
                elif "contribute my knowledge" in question_name:
                    # Handle the checkbox for willing to contribute
                    user_data["willing_to_contribute"] = bool(value)
                elif "guide you to" in question_name and isinstance(value, list):
                    # Handle the "Who would you like us to guide you to?" field
                    # Convert list to string with comma delimiter
                    user_data["goals"] = ", ".join(value)
        
        # Extract payment information
        payment_data = None
        
        for payment in payload.submission.payments:
            if payment.name == "Complete checkout" and payment.value and payment.value.status and payment.value.email:
                payment_data = {
                    "email": payment.value.email,
                    "status": payment.value.status,
                    "payment_id": payment.id,
                    "total_amount": payment.value.totalAmount,
                    "currency": payment.value.currency
                }
                break
        
        # Find user by email
        from app.models.base import AuthUser
        from app.models.payment import Payment
        
        user = None
        if user_data.get("email"):
            # Try to find user through email auth
            from app.models.base import EmailUser
            email_user = db.query(EmailUser).filter_by(email=user_data["email"]).first()
            
            if email_user:
                auth_user = db.query(AuthUser).filter_by(id=email_user.auth_id).first()
                if auth_user:
                    user = db.query(UserDB).filter_by(uuid=auth_user.user_uuid).first()
        
        # Update user profile if found
        if user and user_data:
            for key, value in user_data.items():
                if value and hasattr(user, key):
                    setattr(user, key, value)
            db.commit()
            logger.info(f"Updated user profile for {user.uuid}")
        
        # Record payment information
        if payment_data:
            # Create payment record
            payment = Payment(
                email=payment_data["email"],
                status=payment_data["status"],
                payment_id=payment_data["payment_id"],
                total_amount=payment_data["total_amount"],
                currency=payment_data["currency"],
                user_id=user.uuid if user else None
            )
            db.add(payment)
            db.commit()
            logger.info(f"Recorded payment: {payment_data}")
        
        return WebhookResponse(success=True, message="Webhook processed successfully")
    
    except Exception as e:
        logger.error(f"Error processing registration webhook: {str(e)}")
        # Don't raise an exception to ensure Fillout gets a 200 response
        return WebhookResponse(success=False, error=str(e))

@router.get("/{fillout_id}/data", response_model=Dict)
async def get_fillout_data(
    fillout_id: str,
    project_id: Optional[str] = None,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data for a specific fillout submission
    """
    # Look for existing data entry
    query = db.query(FilloutData).filter(
        FilloutData.form_id == fillout_id,
        FilloutData.user_id == current_user.uuid
    )
    
    # Add project filter if provided
    if project_id:
        query = query.filter(FilloutData.project_id == uuid.UUID(project_id))
    
    fillout_data = query.first()
    
    if not fillout_data:
        return {"submission_data": []}
    
    # Transform the data for frontend consumption
    submission_data = fillout_data.data
    
    return {"submission_data": submission_data}

@router.post("/{fillout_id}/webhook", response_model=WebhookResponse)
async def fillout_webhook(
    fillout_id: str,
    payload: dict,
    db: Session = Depends(get_db)
):
    """
    Webhook endpoint for receiving fillout form submissions
    """
    try:
        # Extract submission data
        submission_data = payload.get("submission", {})
        user_id_param = None
        
        # Look for user ID in URL parameters
        url_parameters = submission_data.get("urlParameters", [])
        for param in url_parameters:
            if param.get("name") == "userId":
                user_id_param = param.get("value")
                break
        
        if not user_id_param:
            return WebhookResponse(
                success=False,
                error="User ID not found in submission parameters"
            )
        
        # Find the user
        user = db.query(UserDB).filter(UserDB.uuid == uuid.UUID(user_id_param)).first()
        if not user:
            return WebhookResponse(
                success=False,
                error=f"User not found with ID: {user_id_param}"
            )
        
        # Extract project ID if present
        project_id_param = None
        for param in url_parameters:
            if param.get("name") == "projectId":
                project_id_param = param.get("value")
                break
        
        # Store submission data
        questions = submission_data.get("questions", [])
        
        # Check if we already have data for this user and form
        existing_data = db.query(FilloutData).filter(
            FilloutData.user_id == user.uuid,
            FilloutData.form_id == fillout_id
        )
        
        # Add project filter if provided
        if project_id_param:
            existing_data = existing_data.filter(
                FilloutData.project_id == uuid.UUID(project_id_param)
            )
        
        existing_data = existing_data.first()

        if existing_data:
            # Update the existing record
            existing_data.data = questions
            existing_data.updated_at = datetime.now(timezone.utc)
            logger.info(f"Updated existing fillout data for user {user_id_param}, form {fillout_id}")
        else:
            # Create new record
            fillout_data = FilloutData(
                user_id=user.uuid,
                form_id=fillout_id,
                data=questions
            )
            
            # Add project ID if provided
            if project_id_param:
                fillout_data.project_id = uuid.UUID(project_id_param)
            
            db.add(fillout_data)
            logger.info(f"Created new fillout data record for user {user_id_param}, form {fillout_id}")
        
        # Mark the submission as completed
        submission_query = db.query(FilloutSubmission).filter(
            FilloutSubmission.user_id == user.uuid,
            FilloutSubmission.fillout_id == fillout_id
        )
        
        # Add project filter if provided
        if project_id_param:
            submission_query = submission_query.filter(
                FilloutSubmission.project_id == uuid.UUID(project_id_param)
            )
        
        submission = submission_query.first()
        
        if submission:
            # Update existing submission
            submission.submitted_at = datetime.now(timezone.utc)
            logger.info(f"Marked existing submission as completed for user {user_id_param}, form {fillout_id}")
        else:
            # Create a new submission record
            new_submission = FilloutSubmission(
                user_id=user.uuid,
                fillout_id=fillout_id,
                started_at=datetime.now(timezone.utc),
                submitted_at=datetime.now(timezone.utc)
            )
            
            # Add project ID if provided
            if project_id_param:
                new_submission.project_id = uuid.UUID(project_id_param)
            
            db.add(new_submission)
            logger.info(f"Created and completed new submission for user {user_id_param}, form {fillout_id}")
        
        db.commit()
        
        return WebhookResponse(
            success=True,
            message="Fillout submission processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Error processing fillout webhook: {str(e)}")
        logger.error(traceback.format_exc())
        return WebhookResponse(
            success=False,
            error=f"Error processing submission: {str(e)}"
        )

@router.post("/{fillout_id}/request-validation")
async def request_form_validation(
    fillout_id: str,
    request_data: dict = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Request validation for a completed form submission.
    
    Sets the requested_at timestamp for a form submission.
    """
    project_id = request_data.get("projectId")
    
    # Find the submission
    submission_query = db.query(FilloutSubmission).filter(
        FilloutSubmission.fillout_id == fillout_id,
        FilloutSubmission.user_id == current_user.uuid
    )
    
    # Add project filter if provided
    if project_id:
        submission_query = submission_query.filter(
            FilloutSubmission.project_id == uuid.UUID(project_id)
        )
    
    submission = submission_query.first()
    
    if not submission:
        # Create a new record if one doesn't exist (unusual case)
        submission = FilloutSubmission(
            user_id=current_user.uuid,
            fillout_id=fillout_id,
            started_at=datetime.now(timezone.utc),
            submitted_at=datetime.now(timezone.utc),
            requested_at=datetime.now(timezone.utc)
        )
        
        # Add project association if provided
        if project_id:
            submission.project_id = uuid.UUID(project_id)
        
        db.add(submission)
        db.commit()
    else:
        if not submission.submitted_at:
            raise HTTPException(
                status_code=400,
                detail="Form must be completed before requesting validation"
            )
        
        # Set requested_at timestamp
        submission.requested_at = datetime.now(timezone.utc)
    db.commit()
    
    return {"status": "success", "message": "Validation requested successfully"}