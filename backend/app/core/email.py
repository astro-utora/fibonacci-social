from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from pathlib import Path
from typing import List

# Email configuration
email_config = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER='app/templates'
)

# Create FastMail instance
mail = FastMail(email_config)

async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    template_name: str | None = None,
    template_data: dict | None = None
) -> None:
    """
    Send email using configured email service
    
    Args:
        recipients: List of email addresses
        subject: Email subject
        body: Plain text body (used if template_name is None)
        template_name: Optional template file name
        template_data: Optional data for template rendering
    """
    # Create message schema
    if template_name and template_data:
        # Use template
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            template_body=template_data,
            subtype="html"
        )
        # Send using template
        await mail.send_message(message, template_name=template_name)
    else:
        # Use plain text
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="plain"
        )
        # Send plain text
        await mail.send_message(message)

async def send_verification_email(email: str, token: str) -> None:
    """Send email verification link"""
    await send_email(
        recipients=[email],
        subject="Verify your email",
        template_name="verification.html",
        template_data={
            "verify_url": f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
        }
    )

async def send_password_reset_email(email: str, token: str) -> None:
    """Send password reset link"""
    await send_email(
        recipients=[email],
        subject="Reset your password",
        template_name="reset_password.html",
        template_data={
            "reset_url": f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"
        }
    ) 