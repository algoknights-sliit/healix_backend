from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
from app.models.health_metric import AnatomyCategory

class HealthMetricBase(BaseModel):
    metric_name: str
    value: float
    unit: Optional[str] = None
    anatomy_category: Optional[AnatomyCategory] = None
    recorded_at: Optional[datetime] = None

class HealthMetricCreate(HealthMetricBase):
    user_id: UUID

class HealthMetricUpdate(BaseModel):
    metric_name: Optional[str] = None
    value: Optional[float] = None
    unit: Optional[str] = None
    anatomy_category: Optional[AnatomyCategory] = None
    recorded_at: Optional[datetime] = None

class HealthMetricRead(HealthMetricBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    flag: str
    created_at: datetime
    updated_at: datetime

class MetricReferenceBase(BaseModel):
    metric_name: str
    threshold_1: Optional[float] = None
    threshold_2: Optional[float] = None
    threshold_3: Optional[float] = None
    threshold_4: Optional[float] = None
    unit: str
    anatomy_category: Optional[AnatomyCategory] = None

class MetricReferenceRead(MetricReferenceBase):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
    updated_at: datetime
