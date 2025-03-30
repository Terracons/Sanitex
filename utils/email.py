from fastapi import BackgroundTasks
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from jose import jwt
from dotenv import dotenv_values
from models import User
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from sqlalchemy.orm import Session
from jinja2 import Template

# Load environment variables
config_credentials = dotenv_values(".env")
SECRET_KEY = config_credentials["SECRET_KEY"]
ALGORITHM = config_credentials["ALGORITHM"]

# Email Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=config_credentials["EMAIL"],
    MAIL_PASSWORD=config_credentials["PASSWORD"],
    MAIL_FROM=config_credentials["EMAIL"],
    MAIL_PORT=465,  # Port 465 for SSL
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,  # False for SSL
    MAIL_SSL_TLS=True,  # True for SSL
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER="templates"  # Ensure template folder exists
)

# Initialize Jinja2Templates
templates = Jinja2Templates(directory="templates")

# ✅ Generate Email Verification Token
def generate_email_token(user: User):
    token_data = {"id": str(user.id), "email": user.email}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return token

# ✅ Send Verification Email
async def send_email_verification(user: User, request: Request):
    token = generate_email_token(user)
    verification_link = f"{str(request.base_url).rstrip('/')}/auth/confirm-email/{token}"
    # Render email template with Jinja2
    email_body = templates.get_template("email_verification.html").render(
        full_name=user.full_name,
        verification_link=verification_link
    )

    # Prepare Email
    message = MessageSchema(
        subject="Email Verification",
        recipients=[user.email],
        body=email_body,
        subtype=MessageType.html
    )

    # Send Email in Background
    fm = FastMail(conf)
    await fm.send_message(message)

    return {"message": "Verification email sent"}

async def send_welcome_email(user_email: str, db_session: Session, background_tasks: BackgroundTasks):
    user = db_session.query(User).filter(User.email == user_email).first()

    if not user:
        print("User not found")  # Log error instead of returning a response
        return

    # Render welcome email template with Jinja2
    email_body = templates.get_template("welcome_email.html").render(
        full_name=user.full_name
    )

    # Prepare Email
    message = MessageSchema(
        subject="Welcome to Our Platform!",
        recipients=[user.email],
        body=email_body,
        subtype=MessageType.html
    )

    # Send Email in Background
    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)



async def send_reset_password_email(user_email: str, db_session: Session, token: str):
    reset_link = f"http://127.0.0.1:8000/auth/reset-password?token={token}"
    user = db_session.query(User).filter(User.email == user_email).first()

    if not user:
        print("User not found")
        return

    # Load email template using Jinja2
    email_template = Template("""
    <h1>Password Reset Request</h1>
    <p>Click the link below to reset your password:</p>
    <a href="{{ reset_link }}">Reset Password</a>
    """)

    email_body = email_template.render(reset_link=reset_link)

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[user.email],
        body=email_body,
        subtype=MessageType.html,
    )

    fm = FastMail(conf)
    await fm.send_message(message)  # Now it's a synchronous function