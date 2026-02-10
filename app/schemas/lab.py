# app/schemas/lab.py
from pydantic import BaseModel

class LabCreate(BaseModel):
    name: str
    location: str
    phone: str

class LabOut(BaseModel):
    id: int
    name: str
    location: str
    phone: str

    class Config:
        orm_mode = True
