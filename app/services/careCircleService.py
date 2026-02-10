# app/services/careCircleService.py
from app.db.supabase import supabase
from app.schemas.care_circle_member import CareCircleMemberCreate, CareCircleMemberUpdate
from typing import Optional

def create_care_circle_member(member: CareCircleMemberCreate) -> dict:
    """Create a new care circle member"""
    try:
        # Check if email already exists
        existing = supabase.table("care_circle_members").select("email").eq("email", member.email).execute()
        if existing.data:
            return {"success": False, "error": "Email already exists in care circle"}
        
        # Insert member data
        response = supabase.table("care_circle_members").insert({
            "name": member.name,
            "email": member.email
        }).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Failed to create member"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_care_circle_member_by_id(member_id: str) -> Optional[dict]:
    """Get a care circle member by UUID"""
    try:
        response = supabase.table("care_circle_members").select("*").eq("id", member_id).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Member not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def get_care_circle_member_by_email(email: str) -> Optional[dict]:
    """Get a care circle member by email"""
    try:
        response = supabase.table("care_circle_members").select("*").eq("email", email).execute()
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Member not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def list_care_circle_members(skip: int = 0, limit: int = 100) -> dict:
    """List all care circle members with pagination"""
    try:
        response = supabase.table("care_circle_members").select("*").range(skip, skip + limit - 1).order("created_at", desc=True).execute()
        return {"success": True, "data": response.data, "count": len(response.data)}
    except Exception as e:
        return {"success": False, "error": str(e)}

def update_care_circle_member(member_id: str, updates: CareCircleMemberUpdate) -> dict:
    """Update a care circle member"""
    try:
        # Only include non-None fields in the update
        update_data = {k: v for k, v in updates.dict().items() if v is not None}
        
        if not update_data:
            return {"success": False, "error": "No fields to update"}
        
        # Check if email is being updated and if it already exists
        if 'email' in update_data:
            existing = supabase.table("care_circle_members").select("id").eq("email", update_data['email']).execute()
            if existing.data and existing.data[0]['id'] != member_id:
                return {"success": False, "error": "Email already in use"}
        
        response = supabase.table("care_circle_members").update(update_data).eq("id", member_id).execute()
        
        if response.data:
            return {"success": True, "data": response.data[0]}
        return {"success": False, "error": "Member not found or update failed"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def delete_care_circle_member(member_id: str) -> dict:
    """Delete a care circle member"""
    try:
        response = supabase.table("care_circle_members").delete().eq("id", member_id).execute()
        return {"success": True, "message": "Member deleted successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}
