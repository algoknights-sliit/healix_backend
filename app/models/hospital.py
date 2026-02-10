from app.core.database import Base
from sqlalchemy import Column, Integer, String

class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    location = Column(String, nullable=False)
    phone = Column(String, nullable=False, unique=True)
