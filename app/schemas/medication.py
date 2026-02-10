# app/schemas/medication.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class MedicationCreate(BaseModel):
    """Schema for creating a new medication"""
    patient_id: UUID = Field(..., description="Patient UUID")
    name: str = Field(..., min_length=1, max_length=100, description="Medication name")
    dosage_mg: int = Field(..., gt=0, description="Dosage in milligrams (must be positive)")
    frequency_per_day: int = Field(..., gt=0, le=24, description="Frequency per day (1-24)")
    instructions: Optional[str] = Field(None, description="Additional instructions")

class MedicationUpdate(BaseModel):
    """Schema for updating medication information (partial updates allowed)"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    dosage_mg: Optional[int] = Field(None, gt=0)
    frequency_per_day: Optional[int] = Field(None, gt=0, le=24)
    instructions: Optional[str] = None

class MedicationOut(BaseModel):
    """Schema for medication response"""
    id: UUID
    patient_id: UUID
    name: str
    dosage_mg: int
    frequency_per_day: int
    instructions: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic v2
