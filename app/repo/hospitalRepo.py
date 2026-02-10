from sqlalchemy.orm import Session
from app.models.hospital import Hospital

def create_hospital(db: Session, hospital: Hospital) -> Hospital:
    db.add(hospital)
    db.commit()
    db.refresh(hospital)
    return hospital

def get_hospital(db: Session, hospital_id: int) -> Hospital | None:
    return db.query(Hospital).filter(Hospital.id == hospital_id).first()

def get_hospitals(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Hospital).offset(skip).limit(limit).all()

def update_hospital(db: Session, hospital: Hospital, updates: dict) -> Hospital:
    for key, value in updates.items():
        setattr(hospital, key, value)
    db.commit()
    db.refresh(hospital)
    return hospital

def delete_hospital(db: Session, hospital: Hospital):
    db.delete(hospital)
    db.commit()
    return {"message": "Hospital deleted successfully"}
