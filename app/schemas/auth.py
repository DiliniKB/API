from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, time
from uuid import UUID

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: UUID
    email: str
    name: Optional[str]
    birth_date: Optional[date]
    birth_time: Optional[time]
    birth_location: Optional[str]
    timezone: str
    
    class Config:
        from_attributes = True