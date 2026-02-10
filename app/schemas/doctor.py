from pydantic import BaseModel

class DoctorCreate(BaseModel):
  fname: str
  lname: str
  phone: str
  specilty: str

class DoctorUpdate(BaseModel):
  fname: str | None = None
  lname: str | None = None
  phone: str | None = None
  specilty: str | None = None

class DoctorOut(BaseModel):
  id: int
  fname: str
  lname: str
  phone: str
  specilty: str

  class Config:
    orm_mode = True