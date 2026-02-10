# app/repo/labRepo.py
from sqlalchemy.orm import Session
from app.models.lab import Lab

def create_lab(db: Session, lab: Lab) -> Lab:
    db.add(lab)
    db.commit()
    db.refresh(lab)
    return lab

def get_lab(db: Session, lab_id: int) -> Lab | None:
    return db.query(Lab).filter(Lab.id == lab_id).first()

def get_labs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Lab).offset(skip).limit(limit).all()

def update_lab(db: Session, lab: Lab, updates: dict) -> Lab:
    for key, value in updates.items():
        setattr(lab, key, value)
    db.commit()
    db.refresh(lab)
    return lab

def delete_lab(db: Session, lab: Lab):
    db.delete(lab)
    db.commit()
    return {"message": "Lab deleted successfully"}
