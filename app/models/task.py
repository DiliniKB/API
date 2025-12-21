from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    list_id = Column(UUID(as_uuid=True), ForeignKey("lists.id", ondelete="CASCADE"), nullable=False)
    
    title = Column(Text, nullable=False)
    description = Column(Text)
    deadline = Column(DateTime(timezone=True))
    
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime(timezone=True))
    priority = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    list = relationship("List", back_populates="tasks")