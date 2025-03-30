from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status, Form,Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserResponse, Token, ForgotPasswordRequest, ResetPasswordRequest, ForgotPasswordRequest
from models import User
from utils.security import hash_password, get_current_user, create_access_token, authenticate_user
from utils.email import send_email_verification, send_welcome_email, send_reset_password_email
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv
import os

load_dotenv()  


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
router = APIRouter()

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        phone=user_data.phone,
        password = hash_password(user_data.password),
        is_verified=False  # ✅ User starts as unverified
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # ✅ Send verification email in the background
    background_tasks.add_task(send_email_verification, new_user, request)

    return new_user

templates = Jinja2Templates(directory="templates")

@router.get("/confirm-email/{token}", response_class=HTMLResponse)
def confirm_email(
    request: Request, 
    token: str, 
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")

        if not email:
            return templates.TemplateResponse("email_confirmation.html", {"request": request, "status": "error", "message": "Invalid Token"})

        user = db.query(User).filter(User.email == email).first()

        if not user:
            return templates.TemplateResponse("email_confirmation.html", {"request": request, "status": "error", "message": "User Not Found"})

        if user.is_verified:
            return templates.TemplateResponse("email_confirmation.html", {"request": request, "status": "info", "message": "Email Already Verified"})

        user.is_verified = True
        db.commit()

        # Send welcome email in the background
        background_tasks.add_task(send_welcome_email, user.email, db, background_tasks)

        # ✅ Return an HTML response using the Jinja2 template
        return templates.TemplateResponse("email_confirmation.html", {"request": request, "status": "success", "message": "Email Verified Successfully!"})

    except JWTError:
        return templates.TemplateResponse("email_confirmation.html", {"request": request, "status": "error", "message": "Invalid or Expired Token"})
    
@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me")
def get_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "is_verified": current_user.is_verified,
    }


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate password reset token
    reset_token = create_access_token({"sub": user.email})

    # Send reset password email in the background (sync function)
    background_tasks.add_task(send_reset_password_email, user.email, db, reset_token)

    return {"message": "Password reset email sent. Check your inbox."}



@router.api_route("/reset-password", methods=["GET", "POST"], response_class=HTMLResponse)
async def reset_password(request: Request, db: Session = Depends(get_db), token: str = Query(None), new_password: str = Form(None)):
    if request.method == "GET":
        print("Rendering Form with Token:", token)  # Debugging
        return templates.TemplateResponse("reset_password.html", {"request": request, "token": token})
    if request.method == "POST":
        form_data = await request.form() 
        token = form_data.get("token")  # Extract token from form
        print("Received Token:", token)
        print("Received New Password:", new_password)
        if not token or not new_password:
            raise HTTPException(status_code=400, detail="Invalid request")

        try:
            # Decode JWT token
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_email: str = payload.get("sub")
            if user_email is None:
                raise HTTPException(status_code=400, detail="Invalid token")
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid or expired token")
        
        # Find user by email
        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update password
        user.password = hash_password(new_password)
        db.commit()
        return RedirectResponse(url="/auth/login", status_code=303)
