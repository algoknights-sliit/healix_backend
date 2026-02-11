# app/models/care_circle_member.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class CareCircleMember:
    """
    Care Circle Member model matching Supabase schema.
    Note: This is for documentation only.
    The actual database schema is managed by Supabase.
    """
    id: UUID
    patient_id: UUID
    name: str
    email: str
    created_at: datetime
