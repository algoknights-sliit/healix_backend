from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.services.doctorService import (
  create_doctor as service_create_doctor,
  get_doctor_by_id,
  list_doctors,
  update_doctor_by_id,
  delete_doctor_by_id
)

router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/create", response_model=DoctorOut)
def create(data: DoctorCreate, db: Session = Depends(get_db)):
  return service_create_doctor(db, data)

@router.get("/{doctor_id}", response_model=DoctorOut)
def read(doctor_id: int, db: Session = Depends(get_db)):
  return get_doctor_by_id(db, doctor_id)

@router.get("/", response_model=list[DoctorOut])
def read_all(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
  return list_doctors(db, skip=skip, limit=limit)

@router.put("/{doctor_id}", response_model=DoctorOut)
def update(doctor_id: int, updates: DoctorUpdate, db: Session = Depends(get_db)):
  return update_doctor_by_id(db, doctor_id, updates)

@router.delete("/{doctor_id}")
def delete(doctor_id: int, db: Session = Depends(get_db)):
  return delete_doctor_by_id(db, doctor_id)
