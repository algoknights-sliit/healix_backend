# app/repo/patientRepo.py
from sqlalchemy.orm import Session
from app.models.patient import Patient

def create_patient(db: Session, patient: Patient) -> Patient:
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient

def get_patient(db: Session, patient_id: int) -> Patient | None:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patients(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Patient).offset(skip).limit(limit).all()

def update_patient(db: Session, patient: Patient, updates: dict) -> Patient:
    for key, value in updates.items():
        setattr(patient, key, value)
    db.commit()
    db.refresh(patient)
    return patient

def delete_patient(db: Session, patient: Patient):
    db.delete(patient)
    db.commit()
    return {"message": "Patient deleted successfully"}
