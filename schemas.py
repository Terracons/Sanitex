from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional

# ===========================
# 🔹 AUTHENTICATION SCHEMAS
# ===========================
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

# ===========================
# 🔹 USER SCHEMA
# ===========================
class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True  # Allows ORM serialization

# ===========================
# 🔹 WORKER SCHEMA
# ===========================
class WorkerCreate(BaseModel):
    full_name: str
    phone: str
    email: EmailStr

class WorkerResponse(WorkerCreate):
    id: int
    availability: str
    rating: float
    created_at: datetime

    class Config:
        from_attributes = True

# ===========================
# 🔹 BOOKING SCHEMA
# ===========================
class BookingCreate(BaseModel):
    service_type: str  # "cleaning", "fumigation"
    address: str
    booking_date: datetime
    price: float
    special_requests: Optional[str] = None

class BookingResponse(BookingCreate):
    id: int
    user_id: int
    worker_id: Optional[int] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

# ===========================
# 🔹 PRICING SCHEMA
# ===========================
class PricingCreate(BaseModel):
    service_type: str
    location: str
    base_price: float
    demand_factor: float
    final_price: float

class PricingResponse(PricingCreate):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

# ===========================
# 🔹 REVIEW SCHEMA
# ===========================
class ReviewCreate(BaseModel):
    booking_id: int
    user_id: int
    worker_id: int
    rating: conint(ge=1, le=5)  # Rating should be between 1 and 5
    review_text: Optional[str] = None

class ReviewResponse(ReviewCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordRequest(BaseModel):
    new_password: str

class UserUpdate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

class WorkerUpdate(BaseModel):
    full_name: Optional[str] = None
    availability: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    email: EmailStr
