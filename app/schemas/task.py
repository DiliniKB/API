from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class TaskCreate(BaseModel):
    title: str
    list_id: UUID
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = 0

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: Optional[int] = None
    completed: Optional[bool] = None

class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    list_id: UUID
    title: str
    description: Optional[str]
    deadline: Optional[datetime]
    completed: bool
    completed_at: Optional[datetime]
    priority: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class ListCreate(BaseModel):
    name: str
    is_default: bool = False

class ListResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    is_default: bool
    created_at: datetime
    
    class Config:
        from_attributes = True