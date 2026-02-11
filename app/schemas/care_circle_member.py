# app/schemas/care_circle_member.py
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class CareCircleMemberCreate(BaseModel):
    """Schema for creating a new care circle member"""
    patient_id: UUID = Field(..., description="ID of the patient this member belongs to")
    name: str = Field(..., min_length=1, max_length=100, description="Member's full name")
    email: EmailStr = Field(..., description="Member's email address (must be unique)")

class CareCircleMemberUpdate(BaseModel):
    """Schema for updating care circle member information (partial updates allowed)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None

class CareCircleMemberOut(BaseModel):
    """Schema for care circle member response"""
    id: UUID
    patient_id: UUID
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2
