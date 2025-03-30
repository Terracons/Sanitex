from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth,users,workers,booking,reviews
import uvicorn
from mangum import Mangum

# ===========================
# 🔹 Initialize FastAPI App
# ===========================
app = FastAPI(title="AI-Driven House Cleaning & Fumigation Booking API",
              description="Manage users, bookings, pricing, AI chat, and more.",
              version="1.0.0")
handler = Mangum(app)
# ===========================
# 🔹 Database Setup
# ===========================
Base.metadata.create_all(bind=engine)  # Auto-create tables if not existing

# ===========================
# 🔹 CORS Middleware
# ===========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# 🔹 Include Routers
# ===========================
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(workers.router, prefix="/workers", tags=["Workers"])
app.include_router(booking.router, prefix="/bookings", tags=["Bookings"])
app.include_router(reviews.router, prefix="/reviews",tags=["Reviews"])

# ===========================
# 🔹 Root Endpoint
# ===========================
@app.get("/", tags=["Root"])
def root():
    return {"message": "Welcome to the AI-Driven House Cleaning & Fumigation API 🚀"}

# ===========================
# 🔹 Run the App
# ===========================
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

