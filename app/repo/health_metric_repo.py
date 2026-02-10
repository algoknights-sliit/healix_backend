from sqlalchemy.orm import Session
from app.models.health_metric import HealthMetric, AnatomyCategory, MetricReference
from app.schemas.health_metric import HealthMetricCreate, HealthMetricUpdate, MetricReferenceBase
from uuid import UUID
from typing import List, Optional

class HealthMetricRepo:
    @staticmethod
    def create(db: Session, metric_in: HealthMetricCreate) -> HealthMetric:
        db_metric = HealthMetric(**metric_in.model_dump())
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric

    @staticmethod
    def get_by_id(db: Session, metric_id: UUID) -> Optional[HealthMetric]:
        return db.query(HealthMetric).filter(HealthMetric.id == metric_id).first()

    def get_multi(db: Session, user_id: UUID, anatomy_category: Optional[AnatomyCategory] = None, skip: int = 0, limit: int = 100):
        query = db.query(HealthMetric).filter(HealthMetric.user_id == user_id)
        if anatomy_category is not None:
            query = query.filter(HealthMetric.anatomy_category == anatomy_category)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def update(db: Session, db_metric: HealthMetric, metric_in: HealthMetricUpdate) -> HealthMetric:
        update_data = metric_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_metric, key, value)
        db.add(db_metric)
        db.commit()
        db.refresh(db_metric)
        return db_metric

    @staticmethod
    def delete(db: Session, metric_id: UUID) -> bool:
        db_metric = db.query(HealthMetric).filter(HealthMetric.id == metric_id).first()
        if db_metric:
            db.delete(db_metric)
            db.commit()
            return True
        return False

class MetricReferenceRepo:
    @staticmethod
    def create_or_update(db: Session, ref_in: MetricReferenceBase) -> MetricReference:
        db_ref = db.query(MetricReference).filter(MetricReference.metric_name == ref_in.metric_name).first()
        if db_ref:
            for key, value in ref_in.model_dump().items():
                setattr(db_ref, key, value)
        else:
            db_ref = MetricReference(**ref_in.model_dump())
            db.add(db_ref)
        db.commit()
        db.refresh(db_ref)
        return db_ref

    @staticmethod
    def get_by_name(db: Session, metric_name: str) -> Optional[MetricReference]:
        return db.query(MetricReference).filter(MetricReference.metric_name == metric_name).first()

    @staticmethod
    def get_all(db: Session) -> List[MetricReference]:
        return db.query(MetricReference).all()
