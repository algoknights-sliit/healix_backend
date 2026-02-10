from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from app.schemas.health_metric import HealthMetricCreate, HealthMetricUpdate, HealthMetricRead
from app.services.health_metric_service import HealthMetricService
from app.models.health_metric import AnatomyCategory
from app.core.database import get_db
from uuid import UUID
from typing import List, Optional

router = APIRouter(prefix="/health", tags=["Health Metrics"])

@router.post("/", response_model=HealthMetricRead, status_code=status.HTTP_201_CREATED)
def create_health_metric(
    metric_in: HealthMetricCreate,
    db: Session = Depends(get_db)
):
    return HealthMetricService.create_metric(db, metric_in)

@router.get("/", response_model=List[HealthMetricRead])
def get_health_metrics(
    user_id: UUID,
    anatomy_category: Optional[AnatomyCategory] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    return HealthMetricService.get_user_metrics(db, user_id, anatomy_category, skip, limit)

@router.get("/{metric_id}", response_model=HealthMetricRead)
def get_health_metric(
    metric_id: UUID,
    db: Session = Depends(get_db)
):
    return HealthMetricService.get_metric(db, metric_id)

@router.put("/{metric_id}", response_model=HealthMetricRead)
def update_health_metric(
    metric_id: UUID,
    metric_in: HealthMetricUpdate,
    db: Session = Depends(get_db)
):
    return HealthMetricService.update_metric(db, metric_id, metric_in)

@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_health_metric(
    metric_id: UUID,
    db: Session = Depends(get_db)
):
    HealthMetricService.delete_metric(db, metric_id)
    return None
