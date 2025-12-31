from sqlalchemy import Column, String, Time, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy import DateTime
import uuid
from app.database import Base

class ContextWindow(Base):
    __tablename__ = "context_windows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    window_type = Column(String(50), nullable=False)
    # Values: 'work_hours', 'morning_routine', 'evening_wind_down', 'weekend', 'focus_block'
    
    start_time = Column(Time)
    end_time = Column(Time)
    days_of_week = Column(ARRAY(Integer))  # [1,2,3,4,5] for Mon-Fri
    
    energy_level = Column(String(20))  # 'high', 'medium', 'low'
    preferred_activities = Column(ARRAY(String))  # What fits this window
    
    extra_data = Column(JSONB, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="context_windows") 