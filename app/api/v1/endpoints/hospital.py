from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.hospital import HospitalCreate, HospitalOut
from app.services.hospitalService import (
    create_hospital as service_create_hospital,
    get_hospital_by_id,
    list_hospitals,
    update_hospital_service,
    delete_hospital_service,
)
from app.core.database import get_db

router = APIRouter(prefix="/hospitals", tags=["Hospitals"])

@router.post("/create", response_model=HospitalOut)
def create(hospital: HospitalCreate, db: Session = Depends(get_db)):
    return service_create_hospital(db, hospital)

@router.get("/{hospital_id}", response_model=HospitalOut)
def read(hospital_id: int, db: Session = Depends(get_db)):
    hospital = get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital

@router.get("/", response_model=list[HospitalOut])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return list_hospitals(db, skip, limit)

@router.put("/{hospital_id}", response_model=HospitalOut)
def update(hospital_id: int, updates: HospitalCreate, db: Session = Depends(get_db)):
    hospital = get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return update_hospital_service(db, hospital, updates)

@router.delete("/{hospital_id}")
def delete(hospital_id: int, db: Session = Depends(get_db)):
    hospital = get_hospital_by_id(db, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return delete_hospital_service(db, hospital)
