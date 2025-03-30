from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Review, Booking
from schemas import ReviewCreate, ReviewResponse
from database import get_db
from utils.security import get_current_user, get_current_admin
from datetime import datetime
router = APIRouter()

# ✅ Create a Review (Only for Authenticated Users)
@router.post("/create", response_model=ReviewResponse)
def create_review(review: ReviewCreate, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    # Ensure booking exists and belongs to the user
    booking = db.query(Booking).filter(Booking.id == review.booking_id, Booking.user_id == user.id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found or unauthorized")

    # Ensure the booking is completed before reviewing
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="You can only review completed bookings")

    new_review = Review(**review.model_dump(), created_at=datetime.utcnow())
    db.add(new_review)
    db.commit()
    db.refresh(new_review)
    return new_review

# ✅ List All Reviews (Public)
@router.get("/", response_model=list[ReviewResponse])
def list_reviews(db: Session = Depends(get_db)):
    reviews = db.query(Review).all()
    return reviews

# ✅ Get Review by ID (Public)
@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(review_id: int, db: Session = Depends(get_db)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

# ✅ Delete a Review (Admin Only)
@router.delete("/delete/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), admin: dict = Depends(get_current_admin)):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    db.delete(review)
    db.commit()
    return {"message": "Review deleted successfully"}
