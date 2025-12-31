from sqlalchemy import Column, String, Float, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.database import Base

class UserPattern(Base):
    __tablename__ = "user_patterns"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    pattern_type = Column(String(50), nullable=False)
    # Values: 'completion_time', 'procrastination_trigger', 'energy_pattern', 
    #         'work_estimation', 'context_batching', 'preferred_scheduling'
    
    pattern_data = Column(JSONB, nullable=False)  # Flexible storage for insights
    confidence_score = Column(Float, default=0.5)  # 0.0 to 1.0
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_patterns")