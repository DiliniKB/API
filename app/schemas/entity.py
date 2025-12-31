from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID

class EntityCreate(BaseModel):
    entity_type: str = Field(..., description="task, event, goal, milestone, health_log, note")
    title: str
    description: Optional[str] = None
    
    # Temporal
    scheduled_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    
    # Context
    context_tags: List[str] = []
    location: Optional[str] = None
    estimated_duration: Optional[str] = None  # "2 hours", "30 minutes"
    
    # State
    status: str = "pending"
    priority: int = 0
    
    # Metadata
    extra_data: Dict[str, Any] = {}

class EntityUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    due_at: Optional[datetime] = None
    context_tags: Optional[List[str]] = None
    location: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None
    completed_at: Optional[datetime] = None
    extra_data: Optional[Dict[str, Any]] = None

class EntityResponse(BaseModel):
    id: UUID
    user_id: UUID
    entity_type: str
    title: str
    description: Optional[str]
    
    scheduled_at: Optional[datetime]
    due_at: Optional[datetime]
    period_start: Optional[date]
    period_end: Optional[date]
    
    context_tags: List[str]
    location: Optional[str]
    estimated_duration: Optional[timedelta]
    
    status: str
    completed_at: Optional[datetime]
    blocked_by: List[UUID]
    
    priority: int
    extra_data: Dict[str, Any]
    
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class EntityRelationCreate(BaseModel):
    parent_id: UUID
    child_id: UUID
    relation_type: str  # 'subtask', 'prerequisite', 'milestone_of', 'related_to', 'combine_with'

class EntityRelationResponse(BaseModel):
    id: UUID
    parent_id: UUID
    child_id: UUID
    relation_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ContextWindowCreate(BaseModel):
    window_type: str
    start_time: Optional[str] = None  # "09:00:00"
    end_time: Optional[str] = None
    days_of_week: List[int] = []  # [1,2,3,4,5]
    energy_level: Optional[str] = None
    preferred_activities: List[str] = []
    extra_data: Dict[str, Any] = {}

class ContextWindowResponse(BaseModel):
    id: UUID
    user_id: UUID
    window_type: str
    start_time: Optional[str]
    end_time: Optional[str]
    days_of_week: List[int]
    energy_level: Optional[str]
    preferred_activities: List[str]
    extra_data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True