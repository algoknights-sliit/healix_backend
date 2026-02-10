# app/services/medicationService.py
from app.db.supabase import supabase
from app.schemas.medication import MedicationCreate, MedicationUpdate
from typing import Optional

def create_medication(medication: MedicationCreate) -> dict:
    """Create a new medication"""
    try:
        # Insert medication data
        response = supabase.table("medications").insert({
            "patient_id": str(medication.patient_id),
            "name": medication.name,
            "dosage_mg": medication.dosage_mg,
            "frequency_per_day": medication.frequency_per_day,
            "instructions": medication.instructions
        }).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to create medication"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_medication_by_id(medication_id: str) -> Optional[dict]:
    """Get a medication by UUID"""
    try:
        response = supabase.table("medications").select("*").eq("id", medication_id).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Medication not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_medications_by_patient(patient_id: str, skip: int = 0, limit: int = 100) -> dict:
    """Get all medications for a specific patient with pagination"""
    try:
        response = supabase.table("medications").select("*").eq("patient_id", patient_id).range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return {"success": True, "data": response.data, "count": len(response.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_medications(skip: int = 0, limit: int = 100) -> dict:
    """List all medications with pagination"""
    try:
        response = supabase.table("medications").select("*").range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return {"success": True, "data": response.data, "count": len(response.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_medication(medication_id: str, updates: MedicationUpdate) -> dict:
    """Update a medication"""
    try:
        # Only include non-None fields in the update
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            return {"success": False, "error": "No fields to update"}
        
        response = supabase.table("medications").update(update_data).eq("id", medication_id).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Medication not found or update failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_medication(medication_id: str) -> dict:
    """Delete a medication"""
    try:
        response = supabase.table("medications").delete().eq("id", medication_id).execute()
        return {"success": True, "message": "Medication deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}
