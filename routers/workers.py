from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Worker
from schemas import WorkerCreate, WorkerResponse, WorkerUpdate
from utils.security import get_current_user, get_current_admin
from models import User

router = APIRouter()

# ✅ Create a new worker (Users only)
# ✅ Register as a worker (Users only)
@router.post("/workers/register")
async def register_as_worker(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Check if user is already a worker
    if user.role == "worker":
        raise HTTPException(status_code=400, detail="User is already registered as a worker")

    # Update user role to worker
    user.role = "worker"
    db.commit()

    # Create a new entry in the Worker table
    worker = Worker(
        id=user.id,  # Use the same ID as User
        full_name=user.full_name,
        email=user.email,
        phone=user.phone
    )
    db.add(worker)
    db.commit()
    db.refresh(worker)

    return {"message": "You are now registered as a worker", "worker": worker}

# ❌ List all workers (Public)
@router.get("/", response_model=list[WorkerResponse])
async def get_workers(db: Session = Depends(get_db)):
    return db.query(Worker).all()

# ❌ Get a specific worker (Public)
@router.get("/{worker_id}", response_model=WorkerResponse)
async def get_worker(worker_id: int, db: Session = Depends(get_db)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker

# ✅ Update worker details (Users only)
@router.put("/update/{worker_id}", response_model=WorkerResponse)
async def update_worker(
    worker_id: int,
    update_data: WorkerUpdate,
    db: Session = Depends(get_db),
    user: User= Depends(get_current_user)  # Allow authenticated users to update
):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    for key, value in update_data.dict(exclude_unset=True).items():
        setattr(worker, key, value)

    db.commit()
    db.refresh(worker)
    return worker

# ✅ Remove a worker (Admin only)
@router.delete("/delete/{worker_id}")
async def delete_worker(worker_id: int, db: Session = Depends(get_db), admin: User= Depends(get_current_admin)):
    worker = db.query(Worker).filter(Worker.id == worker_id).first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")

    db.delete(worker)
    db.commit()
    return {"message": "Worker deleted successfully"}
