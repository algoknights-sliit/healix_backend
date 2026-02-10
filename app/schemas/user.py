
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.models.user import UserType

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    nic: Optional[str] = None

# Data required to create a user
class UserCreate(UserBase):
    email: EmailStr
    password: str
    nic: str
    user_type: UserType

# Data returned to the client (excludes password)
class UserOut(UserBase):
    id: int
    user_type: UserType
    
    class Config:
        from_attributes = True