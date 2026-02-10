# app/services/patientService.py
from app.db.supabase import supabase
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut, PatientLogin
from app.utils.auth import hash_password, verify_password
from typing import List, Optional
from uuid import UUID

def create_patient(patient: PatientCreate) -> dict:
    """Create a new patient (registration)"""
    try:
        # Hash the password before storing
        password_hash = hash_password(patient.password)
        
        # Check if email already exists
        existing = supabase.table("patients").select("email").eq("email", patient.email).execute()
        if existing.data:
            return {"success": False, "error": "Email already registered"}
        
        # Insert patient data
        response = supabase.table("patients").insert({
            "full_name": patient.full_name,
            "email": patient.email,
            "phone": patient.phone,
            "password_hash": password_hash,
            "nic": patient.nic
        }).execute()
        
        if response.data:
            # Don't return password_hash in response
            patient_data = response.data[0]
            patient_data.pop('password_hash', None)
            return {"success": True, "data": patient_data}
        return {"success": False, "error": "Failed to create patient"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def authenticate_patient(login: PatientLogin) -> dict:
    """Authenticate a patient with email and password"""
    try:
        # Get patient by email
        response = supabase.table("patients").select("*").eq("email", login.email).execute()
        
        if not response.data:
            return {"success": False, "error": "Invalid email or password"}
        
        patient = response.data[0]
        
        # Verify password
        if not verify_password(login.password, patient['password_hash']):
            return {"success": False, "error": "Invalid email or password"}
        
        # Remove password_hash from response
        patient.pop('password_hash', None)
        return {"success": True, "data": patient, "message": "Login successful"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_patient_by_id(patient_id: str) -> Optional[dict]:
    """Get a patient by UUID (excludes password_hash)"""
    try:
        response = supabase.table("patients").select("id, full_name, email, phone, nic, created_at").eq("id", patient_id).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Patient not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_patient_by_email(email: str) -> Optional[dict]:
    """Get a patient by email (excludes password_hash)"""
    try:
        response = supabase.table("patients").select("id, full_name, email, phone, nic, created_at").eq("email", email).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Patient not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_patient_by_nic(nic: str) -> Optional[dict]:
    """Get a patient by NIC (excludes password_hash)"""
    try:
        response = supabase.table("patients").select("id, full_name, email, phone, nic, created_at").eq("nic", nic).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Patient not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_patients(skip: int = 0, limit: int = 100) -> dict:
    """List all patients with pagination (excludes password_hash)"""
    try:
        response = supabase.table("patients").select("id, full_name, email, phone, nic, created_at").range(skip, skip + limit - 1).execute()
        return {"success": True, "data": response.data, "count": len(response.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_patient(patient_id: str, updates: PatientUpdate) -> dict:
    """Update a patient (excludes password updates)"""
    try:
        # Only include non-None fields in the update
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            return {"success": False, "error": "No fields to update"}
        
        # Check if email is being updated and if it already exists
        if 'email' in update_data:
            existing = supabase.table("patients").select("id").eq("email", update_data['email']).execute()
            if existing.data and existing.data[0]['id'] != patient_id:
                return {"success": False, "error": "Email already in use"}
        
        response = supabase.table("patients").update(update_data).eq("id", patient_id).execute()
        
        if response.data:
            # Remove password_hash from response
            patient_data = response.data[0]
            patient_data.pop('password_hash', None)
            return {"success": True, "data": patient_data}
        return {"success": False, "error": "Patient not found or update failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_patient_password(patient_id: str, current_password: str, new_password: str) -> dict:
    """Update patient password after verifying current password"""
    try:
        # Get current patient with password_hash
        patient_response = supabase.table("patients").select("*").eq("id", patient_id).execute()
        
        if not patient_response.data:
            return {"success": False, "error": "Patient not found"}
        
        patient = patient_response.data[0]
        
        # Verify current password
        if not verify_password(current_password, patient['password_hash']):
            return {"success": False, "error": "Current password is incorrect"}
        
        # Hash new password
        new_password_hash = hash_password(new_password)
        
        # Update password
        response = supabase.table("patients").update({
            "password_hash": new_password_hash
        }).eq("id", patient_id).execute()
        
        if response.data:
            return {
                "success": True,
                "message": "Password changed successfully"
            }
        return {"success": False, "error": "Failed to update password"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_patient(patient_id: str) -> dict:

    """Delete a patient"""
    try:
        response = supabase.table("patients").delete().eq("id", patient_id).execute()
        return {"success": True, "message": "Patient deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}
