import uuid
from sqlalchemy import Column, String, DateTime, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base

from datetime import datetime, timedelta, timezone

def get_ist_time():
    return datetime.now(timezone(timedelta(hours=5, minutes=30)))

class ReportExtractedData(Base):
    __tablename__ = "report_extracted_data"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    uhid = Column(UUID(as_uuid=True), index=True, nullable=False)
    report_type = Column(String, index=True, nullable=False)
    extracted_json = Column(JSON, nullable=False)
    raw_text = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=get_ist_time)
    updated_at = Column(DateTime(timezone=True), default=get_ist_time, onupdate=get_ist_time)
