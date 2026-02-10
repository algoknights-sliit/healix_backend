
from sqlalchemy import Column, Integer, String, Boolean, Enum
import enum
from app.db.base_class import Base

class UserType(str, enum.Enum):
    LABS = "LABS"
    DOCTOR = "DOCTOR"
    PATIENT = "PATIENT"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    nic = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    user_type = Column(Enum(UserType), default=UserType.PATIENT, nullable=False)
