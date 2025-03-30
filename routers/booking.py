from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Booking
from schemas import BookingCreate, BookingResponse
from utils.security import get_current_admin, get_current_user
from typing import List

router = APIRouter()

# ✅ Create a new booking (User Only)
@router.post("/create", response_model=BookingResponse)
def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    new_booking = Booking(
        user_id=user["id"],  # Authenticated User ID
        service_type=booking_data.service_type,
        address=booking_data.address,
        booking_date=booking_data.booking_date,
        price=booking_data.price,
        status="pending",
    )
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    return new_booking

# ✅ List all bookings (Admin Only)
@router.get("/", response_model=List[BookingResponse])
def list_bookings(db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    return db.query(Booking).all()

# ✅ Get details of a specific booking (User Only)
@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user["id"]).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

# ✅ Update booking (Admin Only)
@router.put("/update/{booking_id}", response_model=BookingResponse)
def update_booking(booking_id: int, booking_data: BookingCreate, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    # Update fields
    for key, value in booking_data.dict().items():
        setattr(booking, key, value)

    db.commit()
    db.refresh(booking)
    return booking

# ✅ Cancel a booking (User Only)
@router.delete("/cancel/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == user["id"]).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    booking.status = "cancelled"
    db.commit()
    return {"message": "Booking cancelled successfully"}
