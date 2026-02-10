# app/api/v1/endpoints/medication.py
from fastapi import APIRouter, HTTPException
from app.schemas.medication import MedicationCreate, MedicationUpdate, MedicationOut
from app.services.medicationService import (
    create_medication,
    get_medication_by_id,
    get_medications_by_patient,
    list_medications,
    update_medication,
    delete_medication
)
from typing import List

router = APIRouter(prefix="/medications", tags=["Medications"])

# Create
@router.post("/", status_code=201)
def add_medication(medication: MedicationCreate):
    """Add a new medication"""
    result = create_medication(medication)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to add medication"))
    return result

# Read all
@router.get("/")
def get_all_medications(skip: int = 0, limit: int = 100):
    """List all medications with pagination"""
    result = list_medications(skip, limit)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to retrieve medications"))
    return result

# Read by patient
@router.get("/patient/{patient_id}")
def get_patient_medications(patient_id: str, skip: int = 0, limit: int = 100):
    """Get all medications for a specific patient"""
    result = get_medications_by_patient(patient_id, skip, limit)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to retrieve medications"))
    return result

# Read single by ID
@router.get("/{medication_id}")
def get_medication(medication_id: str):
    """Get a medication by UUID"""
    result = get_medication_by_id(medication_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Medication not found"))
    return result

# Update
@router.patch("/{medication_id}")
def update_medication_endpoint(medication_id: str, updates: MedicationUpdate):
    """Update medication information"""
    result = update_medication(medication_id, updates)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to update medication"))
    return result

# Delete
@router.delete("/{medication_id}")
def remove_medication(medication_id: str):
    """Remove a medication"""
    result = delete_medication(medication_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to delete medication"))
    return result
