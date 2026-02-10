# app/services/labService.py
from sqlalchemy.orm import Session
from app.models.lab import Lab
from app.schemas.lab import LabCreate, LabOut
from app.repo.labRepo import (
    create_lab as repo_create_lab,
    get_lab as repo_get_lab,
    get_labs as repo_get_labs,
    update_lab as repo_update_lab,
    delete_lab as repo_delete_lab
)

def create_lab(db: Session, lab: LabCreate) -> LabOut:
    db_lab = Lab(
        name=lab.name,
        location=lab.location,
        phone=lab.phone
    )
    return repo_create_lab(db, db_lab)

def get_lab_by_id(db: Session, lab_id: int) -> LabOut | None:
    return repo_get_lab(db, lab_id)

def list_labs(db: Session, skip: int = 0, limit: int = 100):
    return repo_get_labs(db, skip, limit)

def update_lab_service(db: Session, lab: Lab, updates: LabCreate) -> LabOut:
    updates_dict = updates.dict(exclude_unset=True)
    return repo_update_lab(db, lab, updates_dict)

def delete_lab_service(db: Session, lab: Lab):
    return repo_delete_lab(db, lab)
