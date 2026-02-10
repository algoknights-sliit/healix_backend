# app/schemas/patient.py
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
from uuid import UUID

class PatientCreate(BaseModel):
    """Schema for creating a new patient (registration)"""
    full_name: str = Field(..., min_length=1, max_length=255, description="Patient's full name")
    email: EmailStr = Field(..., description="Patient's email address (must be unique)")
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$', description="Patient's phone number (optional)")
    password: str = Field(..., min_length=8, description="Patient's password (min 8 characters)")
    nic: Optional[str] = Field(None, description="National Identity Card number (optional)")

class PatientUpdate(BaseModel):
    """Schema for updating patient information (partial updates allowed)"""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    nic: Optional[str] = None
    # Note: password updates should be handled separately with proper verification

class PatientPasswordUpdate(BaseModel):
    """Schema for updating patient password"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")

class PatientOut(BaseModel):
    """Schema for patient response (excludes sensitive data)"""
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    nic: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2

class PatientLogin(BaseModel):
    """Schema for patient login"""
    email: EmailStr = Field(..., description="Patient's email address")
    password: str = Field(..., description="Patient's password")
