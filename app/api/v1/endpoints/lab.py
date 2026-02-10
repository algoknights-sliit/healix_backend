# app/api/v1/endpoints/lab.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.lab import LabCreate, LabOut
from app.services.labService import (
    create_lab as service_create_lab,
    get_lab_by_id,
    list_labs,
    update_lab_service,
    delete_lab_service
)
from app.core.database import get_db

router = APIRouter(prefix="/labs", tags=["Labs"])

# Create
@router.post("/create", response_model=LabOut)
def create(lab: LabCreate, db: Session = Depends(get_db)):
    return service_create_lab(db, lab)

# Read single
@router.get("/{lab_id}", response_model=LabOut)
def read(lab_id: int, db: Session = Depends(get_db)):
    lab = get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return lab

# Read all
@router.get("/", response_model=list[LabOut])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_labs(db, skip, limit)

# Update
@router.put("/{lab_id}", response_model=LabOut)
def update(lab_id: int, updates: LabCreate, db: Session = Depends(get_db)):
    lab = get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return update_lab_service(db, lab, updates)

# Delete
@router.delete("/{lab_id}")
def delete(lab_id: int, db: Session = Depends(get_db)):
    lab = get_lab_by_id(db, lab_id)
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    return delete_lab_service(db, lab)
