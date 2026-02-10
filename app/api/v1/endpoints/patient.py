# app/api/v1/endpoints/patient.py
from fastapi import APIRouter, HTTPException, Body
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut, PatientLogin
from app.services.patientService import (
    create_patient,
    authenticate_patient,
    get_patient_by_id,
    get_patient_by_email,
    get_patient_by_nic,
    list_patients,
    update_patient,
    update_patient_password,
    delete_patient
)
from typing import List


router = APIRouter(prefix="/patients", tags=["Patients"])

# Authentication endpoints
@router.post("/register", status_code=201)
def register_patient(patient: PatientCreate):
    """Register a new patient account"""
    result = create_patient(patient)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to register patient"))
    return result

@router.post("/login")
def login_patient(login: PatientLogin):
    """Login with email and password"""
    result = authenticate_patient(login)
    if not result.get("success"):
        raise HTTPException(status_code=401, detail=result.get("error", "Authentication failed"))
    return result

# Read all (must come before /{patient_id})
@router.get("/")
def read_all_patients(skip: int = 0, limit: int = 100):
    """List all patients with pagination"""
    result = list_patients(skip, limit)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to retrieve patients"))
    return result

# Read by email (must come before /{patient_id})
@router.get("/email/{email}")
def read_patient_by_email(email: str):
    """Get a patient by email address"""
    result = get_patient_by_email(email)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Patient not found"))
    return result

# Read by NIC (must come before /{patient_id})
@router.get("/nic/{nic}")
def read_patient_by_nic(nic: str):
    """Get a patient by NIC"""
    result = get_patient_by_nic(nic)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Patient not found"))
    return result

# Read single by ID
@router.get("/{patient_id}")
def read_patient_by_id(patient_id: str):
    """Get a patient by UUID"""
    result = get_patient_by_id(patient_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Patient not found"))
    return result

# Update
@router.patch("/{patient_id}")
def update_patient_endpoint(patient_id: str, updates: PatientUpdate):
    """Update patient information (password updates should use separate endpoint)"""
    result = update_patient(patient_id, updates)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to update patient"))
    return result

# Password Change
@router.patch("/{patient_id}/password")
def change_password_endpoint(
    patient_id: str,
    current_password: str = Body(..., embed=True),
    new_password: str = Body(..., embed=True)
):
    """Change patient password"""
    result = update_patient_password(patient_id, current_password, new_password)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to change password"))
    return result

# Delete
@router.delete("/{patient_id}")

def delete_patient_endpoint(patient_id: str):
    """Delete a patient account"""
    result = delete_patient(patient_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to delete patient"))
    return result
