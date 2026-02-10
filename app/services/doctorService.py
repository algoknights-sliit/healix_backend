from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorCreate, DoctorOut, DoctorUpdate
from app.repo.doctorRepo import create_doctor as repo_create_doctor
from app.repo.doctorRepo import get_doctor as repo_get_doctor
from app.repo.doctorRepo import get_doctors as repo_get_doctors
from app.repo.doctorRepo import update_doctor as repo_update_doctor
from app.repo.doctorRepo import delete_doctor as repo_delete_doctor
from fastapi import HTTPException

def create_doctor(db: Session, doctor: DoctorCreate) -> DoctorOut:
  db_doctor = Doctor(
    fname=doctor.fname,
    lname=doctor.lname,
    phone=doctor.phone,
    specilty=doctor.specilty
  )
  return repo_create_doctor(db, db_doctor)

def get_doctor_by_id(db: Session, doctor_id: int) -> DoctorOut:
  doctor = repo_get_doctor(db, doctor_id)
  if not doctor:
    raise HTTPException(status_code=404, detail="Doctor not found")
  return doctor

def list_doctors(db: Session, skip: int = 0, limit: int = 100):
  return repo_get_doctors(db, skip=skip, limit=limit)

def update_doctor_by_id(db: Session, doctor_id: int, updates: DoctorUpdate) -> DoctorOut:
  doctor = repo_get_doctor(db, doctor_id)
  if not doctor:
    raise HTTPException(status_code=404, detail="Doctor not found")
  updates_dict = updates.dict(exclude_unset=True)
  return repo_update_doctor(db, doctor, updates_dict)

def delete_doctor_by_id(db: Session, doctor_id: int):
  doctor = repo_get_doctor(db, doctor_id)
  if not doctor:
    raise HTTPException(status_code=404, detail="Doctor not found")
  return repo_delete_doctor(db, doctor)
