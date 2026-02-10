# app/schemas/report.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID

class ReportCreate(BaseModel):
    """Schema for creating a new report"""
    patient_id: UUID = Field(..., description="Patient UUID")
    file_id: str = Field(..., description="Unique file identifier from cloud storage")
    report_type: str = Field(..., description="Type of report (e.g., 'FBC', 'Lipid Profile')")
    sample_collected_at: Optional[datetime] = Field(None, description="When sample was collected")
    gcs_path: str = Field(..., description="Google Cloud Storage path to PDF")

class ReportUpdate(BaseModel):
    """Schema for updating report information"""
    report_type: Optional[str] = None
    sample_collected_at: Optional[datetime] = None

class ReportOut(BaseModel):
    """Schema for report response"""
    id: UUID
    patient_id: UUID
    file_id: str
    report_type: str
    sample_collected_at: Optional[datetime]
    gcs_path: str
    created_at: datetime

    class Config:
        from_attributes = True

class BiomarkerCreate(BaseModel):
    """Schema for creating a biomarker"""
    report_id: UUID = Field(..., description="Report UUID this biomarker belongs to")
    name: str = Field(..., description="Biomarker name (e.g., 'Hemoglobin', 'WBC')")
    value: float = Field(..., description="Measured value")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'g/dL', 'cells/μL')")
    ref_min: Optional[float] = Field(None, description="Reference range minimum")
    ref_max: Optional[float] = Field(None, description="Reference range maximum")
    flag: Optional[str] = Field(None, description="Flag: 'HIGH', 'LOW', 'NORMAL', etc.")

class BiomarkerOut(BaseModel):
    """Schema for biomarker response"""
    id: UUID
    report_id: UUID
    name: str
    value: float
    unit: Optional[str]
    ref_min: Optional[float]
    ref_max: Optional[float]
    flag: Optional[str]

    class Config:
        from_attributes = True

class ReportWithBiomarkers(BaseModel):
    """Complete report with all biomarkers"""
    report: ReportOut
    biomarkers: List[BiomarkerOut]

    class Config:
        from_attributes = True
