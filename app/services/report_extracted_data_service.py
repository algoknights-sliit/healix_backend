from sqlalchemy.orm import Session
from app.models.health_metric import AnatomyCategory
from app.models.health_metric import AnatomyCategory
from app.repo.report_extracted_data_repo import ReportExtractedDataRepo
from app.schemas.health_metric import HealthMetricCreate
from app.schemas.report_extracted_data import ReportExtractedDataCreate, ReportExtractedDataUpdate
from app.models.report_extracted_data import ReportExtractedData
from uuid import UUID
from typing import List, Optional
from fastapi import HTTPException, status

from app.services.health_metric_service import HealthMetricService

class ReportExtractedDataService:
    def create_report_data(
        db: Session,
        report_in: ReportExtractedDataCreate
    ) -> ReportExtractedData:

        report = ReportExtractedDataRepo.create(db, report_in)

        # 🔥 Create health metrics AFTER report is saved
        ReportExtractedDataService._create_health_metrics_from_report(
            db=db,
            report=report
        )

        return report

    @staticmethod
    def get_report_data(db: Session, report_id: UUID) -> ReportExtractedData:
        db_report = ReportExtractedDataRepo.get_by_id(db, report_id)
        if not db_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report extracted data not found"
            )
        return db_report

    @staticmethod
    def get_user_report_data(
        db: Session, 
        uhid: UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ReportExtractedData]:
        return ReportExtractedDataRepo.get_multi(db, uhid, skip, limit)

    @staticmethod
    def update_report_data(
        db: Session, 
        report_id: UUID, 
        report_in: ReportExtractedDataUpdate
    ) -> ReportExtractedData:
        db_report = ReportExtractedDataService.get_report_data(db, report_id)
        return ReportExtractedDataRepo.update(db, db_report, report_in)

    @staticmethod
    def delete_report_data(db: Session, report_id: UUID) -> None:
        success = ReportExtractedDataRepo.delete(db, report_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report extracted data not found"
            )
    @staticmethod
    def _create_health_metrics_from_report(
        db: Session,
        report: ReportExtractedData
    ):
        """
        Convert extracted_json into HealthMetric entries
        """
        extracted = report.extracted_json

        if not isinstance(extracted, dict):
            return  # Safety guard

        for metric_name, value in extracted.items():

            # Skip non-numeric values safely
            if not isinstance(value, (int, float)):
                continue
            
            if metric_name in ["Heart Rate", "Systolic BP", "Diastolic BP", "SpO2"]:
                anatomy_category = AnatomyCategory.CHEST
            elif metric_name in ["Blood Glucose", "ALT", "AST", "Bilirubin", "Fasting Plasma Glucose"]:
                anatomy_category = AnatomyCategory.ABDOMEN
            elif metric_name in ["Vision (L)", "Vision (R)", "Hearing Level", "Reaction Time"]:
                anatomy_category = AnatomyCategory.HEAD
            elif metric_name in ["Grip Strength", "Knee Reflex", "Calf Circumference", "Arm Circumference", "Hand Strength"]:
                anatomy_category = AnatomyCategory.LIMBS

            metric_in = HealthMetricCreate(
                user_id=report.uhid,   # assuming uhid == user_id
                metric_name=metric_name,
                value=float(value),
                unit=None,             # auto-filled from reference
                anatomy_category=anatomy_category  # auto-filled from reference
            )

            HealthMetricService.create_metric(db, metric_in)