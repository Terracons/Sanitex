from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import UserCreate, UserResponse, UserUpdate
from models import User
from utils.security import  get_current_user,get_current_admin
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordRequestForm

from dotenv import load_dotenv
import os

load_dotenv()  


SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

router = APIRouter()

@router.get("/users/", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if user.id != user_id :
        raise HTTPException(status_code=403, detail="Not authorized")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# ✅ Update user information
@router.put("/users/update/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if user.id != user_id and user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user_data = db.query(User).filter(User.id == user_id).first()
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(user_data, key, value)

    db.commit()
    db.refresh(user_data)
    return user_data
