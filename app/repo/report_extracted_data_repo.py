from sqlalchemy.orm import Session
from app.models.report_extracted_data import ReportExtractedData
from app.schemas.report_extracted_data import ReportExtractedDataCreate, ReportExtractedDataUpdate
from uuid import UUID
from typing import List, Optional

class ReportExtractedDataRepo:
    @staticmethod
    def create(db: Session, report_in: ReportExtractedDataCreate) -> ReportExtractedData:
        db_report = ReportExtractedData(**report_in.model_dump())
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def get_by_id(db: Session, report_id: UUID) -> Optional[ReportExtractedData]:
        return db.query(ReportExtractedData).filter(ReportExtractedData.id == report_id).first()

    @staticmethod
    def get_multi(
        db: Session, 
        uhid: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ReportExtractedData]:
        return db.query(ReportExtractedData).filter(
            ReportExtractedData.uhid == uhid
        ).offset(skip).limit(limit).all()

    @staticmethod
    def update(
        db: Session, 
        db_report: ReportExtractedData, 
        report_in: ReportExtractedDataUpdate
    ) -> ReportExtractedData:
        update_data = report_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_report, key, value)
        db.add(db_report)
        db.commit()
        db.refresh(db_report)
        return db_report

    @staticmethod
    def delete(db: Session, report_id: UUID) -> bool:
        db_report = db.query(ReportExtractedData).filter(ReportExtractedData.id == report_id).first()
        if db_report:
            db.delete(db_report)
            db.commit()
            return True
        return False
