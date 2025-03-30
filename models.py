from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
from sqlalchemy import Boolean

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(Enum("customer", "worker", "admin", name="user_roles"), default="customer")
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    availability = Column(Enum("available", "busy", name="worker_availability"), default="available")
    rating = Column(Float, default=5.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=True)
    service_type = Column(Enum("cleaning", "fumigation", name="service_types"), nullable=False)
    address = Column(String(255), nullable=False)
    booking_date = Column(DateTime, nullable=False)
    price = Column(Float, nullable=False)
    status = Column(Enum("pending", "confirmed", "completed", "cancelled", name="booking_status"), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    worker = relationship("Worker")

class Pricing(Base):
    __tablename__ = "pricing"

    id = Column(Integer, primary_key=True, index=True)
    service_type = Column(Enum("cleaning", "fumigation", name="service_types"), nullable=False)
    location = Column(String(255), nullable=False)
    base_price = Column(Float, nullable=False)
    demand_factor = Column(Float, default=1.0)
    final_price = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    rating = Column(Float, nullable=False)
    review_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    booking = relationship("Booking")
    user = relationship("User")
    worker = relationship("Worker")
