from sqlalchemy.orm import Session
from app.models.hospital import Hospital
from app.schemas.hospital import HospitalCreate, HospitalOut
from app.repo.hospitalRepo import (
    create_hospital as repo_create_hospital,
    get_hospital as repo_get_hospital,
    get_hospitals as repo_get_hospitals,
    update_hospital as repo_update_hospital,
    delete_hospital as repo_delete_hospital,
)

def create_hospital(db: Session, hospital: HospitalCreate) -> HospitalOut:
    db_hospital = Hospital(
        name=hospital.name,
        location=hospital.location,
        phone=hospital.phone
    )
    return repo_create_hospital(db, db_hospital)

def get_hospital_by_id(db: Session, hospital_id: int) -> HospitalOut | None:
    return repo_get_hospital(db, hospital_id)

def list_hospitals(db: Session, skip: int = 0, limit: int = 100):
    return repo_get_hospitals(db, skip, limit)

def update_hospital_service(db: Session, hospital: Hospital, updates: HospitalCreate) -> HospitalOut:
    updates_dict = updates.dict(exclude_unset=True)
    return repo_update_hospital(db, hospital, updates_dict)

def delete_hospital_service(db: Session, hospital: Hospital):
    return repo_delete_hospital(db, hospital)
