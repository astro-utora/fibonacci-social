from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
import os
from pathlib import Path
from jinja2 import Environment, select_autoescape, FileSystemLoader

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_FROM=os.getenv("MAIL_FROM"),
    MAIL_PORT=int(os.getenv("MAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "templates"
)

# Initialize FastMail
fastmail = FastMail(conf)

# Initialize Jinja2 for email templates
env = Environment(
    loader=FileSystemLoader("app/templates"),
    autoescape=select_autoescape(['html', 'xml'])
)

async def send_verification_email(email: str, token: str):
    """Send verification email to user"""
    # Get verification URL from environment
    verify_url = f"{os.getenv('FRONTEND_URL')}/verify-email?token={token}"
    
    # Render email template
    template = env.get_template("verification.html")
    html = template.render(
        verify_url=verify_url
    )
    
    # Create message
    message = MessageSchema(
        subject="Verify your email",
        recipients=[email],
        body=html,
        subtype="html"
    )
    
    # Send email
    await fastmail.send_message(message) 