# app/models/medication.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

@dataclass
class Medication:
    """
    Medication model matching Supabase schema.
    Note: This is for documentation only.
    The actual database schema is managed by Supabase.
    """
    id: UUID
    patient_id: UUID
    name: str
    dosage_mg: int
    frequency_per_day: int
    instructions: Optional[str]
    created_at: datetime
