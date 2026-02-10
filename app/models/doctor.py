from app.core.database import Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

class Doctor(Base):
  __tablename__="doctors"
  
  id=Column(Integer, primary_key=True, index=True)
  fname=Column(String, nullable=False)
  lname=Column(String, nullable=False)
  phone=Column(String, nullable=False, unique=True)
  specilty=Column(String, nullable=False)