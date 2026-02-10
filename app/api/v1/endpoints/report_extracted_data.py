from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.schemas.report_extracted_data import (
    ReportExtractedDataCreate, 
    ReportExtractedDataUpdate, 
    ReportExtractedDataRead
)
from app.services.report_extracted_data_service import ReportExtractedDataService
from app.core.database import get_db
from uuid import UUID
from typing import List

router = APIRouter(prefix="/report", tags=["Report Extracted Data"])

@router.post("/", response_model=ReportExtractedDataRead, status_code=status.HTTP_201_CREATED)
def create_report_data(
    report_in: ReportExtractedDataCreate,
    db: Session = Depends(get_db)
):
    return ReportExtractedDataService.create_report_data(db, report_in)

@router.get("/", response_model=List[ReportExtractedDataRead])
def get_user_reports(
    uhid: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return ReportExtractedDataService.get_user_report_data(db, uhid, skip, limit)

@router.get("/{report_id}", response_model=ReportExtractedDataRead)
def get_report_data(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    return ReportExtractedDataService.get_report_data(db, report_id)

@router.put("/{report_id}", response_model=ReportExtractedDataRead)
def update_report_data(
    report_id: UUID,
    report_in: ReportExtractedDataUpdate,
    db: Session = Depends(get_db)
):
    return ReportExtractedDataService.update_report_data(db, report_id, report_in)

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_report_data(
    report_id: UUID,
    db: Session = Depends(get_db)
):
    ReportExtractedDataService.delete_report_data(db, report_id)
    return None
