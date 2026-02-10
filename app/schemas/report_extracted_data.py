from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional, Any, Dict

class ReportExtractedDataBase(BaseModel):
    report_type: str
    extracted_json: Dict[str, Any]
    raw_text: Optional[str] = None

class ReportExtractedDataCreate(ReportExtractedDataBase):
    uhid: UUID

class ReportExtractedDataUpdate(BaseModel):
    report_type: Optional[str] = None
    extracted_json: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None

class ReportExtractedDataRead(ReportExtractedDataBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    uhid: UUID
    created_at: datetime
    updated_at: datetime
