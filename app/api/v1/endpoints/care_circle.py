# app/api/v1/endpoints/care_circle.py
from fastapi import APIRouter, HTTPException
from app.schemas.care_circle_member import CareCircleMemberCreate, CareCircleMemberUpdate, CareCircleMemberOut
from app.services.careCircleService import (
    create_care_circle_member,
    get_care_circle_member_by_id,
    get_care_circle_member_by_email,
    list_care_circle_members,
    update_care_circle_member,
    delete_care_circle_member
)
from typing import List, Optional

router = APIRouter(prefix="/care-circle", tags=["Care Circle"])

# Create
@router.post("/members", status_code=201)
def add_member(member: CareCircleMemberCreate):
    """Add a new member to care circle"""
    result = create_care_circle_member(member)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error", "Failed to add member"))
    return result

# Read all
@router.get("/members")
def get_all_members(skip: int = 0, limit: int = 100, patient_id: Optional[str] = None):
    """List all care circle members with pagination"""
    result = list_care_circle_members(skip, limit, patient_id)
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to retrieve members"))
    return result

# Read by email
@router.get("/members/email/{email}")
def get_member_by_email(email: str):
    """Get a care circle member by email address"""
    result = get_care_circle_member_by_email(email)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Member not found"))
    return result

# Read single by ID
@router.get("/members/{member_id}")
def get_member_by_id(member_id: str):
    """Get a care circle member by UUID"""
    result = get_care_circle_member_by_id(member_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Member not found"))
    return result

# Update
@router.patch("/members/{member_id}")
def update_member(member_id: str, updates: CareCircleMemberUpdate):
    """Update care circle member information"""
    result = update_care_circle_member(member_id, updates)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to update member"))
    return result

# Delete
@router.delete("/members/{member_id}")
def remove_member(member_id: str):
    """Remove a member from care circle"""
    result = delete_care_circle_member(member_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("error", "Failed to delete member"))
    return result
