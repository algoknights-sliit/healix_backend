from pydantic import BaseModel

class HospitalCreate(BaseModel):
    name: str
    location: str
    phone: str

class HospitalOut(BaseModel):
    id: int
    name: str
    location: str
    phone: str

    class Config:
        orm_mode = True
