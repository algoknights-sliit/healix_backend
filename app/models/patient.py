# app/models/patient.py
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from typing import Optional

@dataclass
class Patient:
    """
    Patient model matching Supabase schema.
    Note: This is for documentation only.
    The actual database schema is managed by Supabase.
    """
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    password_hash: str
    nic: Optional[str]
    created_at: datetime
    
