from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

class MessageResponse(BaseModel):
    id: UUID
    user_id: UUID
    role: str
    content: str
    extra_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True