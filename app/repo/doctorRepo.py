from typing import List
from sqlalchemy.orm import Session
from app.models.doctor import Doctor
from app.schemas.doctor import DoctorOut, DoctorCreate

def create_doctor(db: Session, doctor: DoctorCreate) -> DoctorOut:
  db.add(doctor)
  db.commit()
  db.refresh(doctor)
  return doctor

def get_doctor(db: Session, doctor_id: int) -> Doctor | None:
  return db.query(Doctor).filter(Doctor.id == doctor_id).first()

def get_doctors(db: Session, skip: int = 0, limit: int = 100) -> List[Doctor]:
  return db.query(Doctor).offset(skip).limit(limit).all()

def update_doctor(db: Session, doctor: Doctor, updates: dict) -> Doctor:
  for key, value in updates.items():
    setattr(doctor, key, value)
  db.commit()
  db.refresh(doctor)
  return doctor

def delete_doctor(db: Session, doctor: Doctor):
  db.delete(doctor)
  db.commit()
  return {"message": "Doctor deleted successfully"}