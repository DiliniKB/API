from sqlalchemy import Column, String, Text, Integer, DateTime, Date, Interval, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class Entity(Base):
    __tablename__ = "entities"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Classification
    entity_type = Column(String(50), nullable=False, index=True)
    # Values: 'task', 'event', 'goal', 'milestone', 'health_log', 'note'
    
    # Content
    title = Column(Text, nullable=False)
    description = Column(Text)
    
    # Temporal (flexible)
    scheduled_at = Column(DateTime(timezone=True), index=True)  # Specific time (events)
    due_at = Column(DateTime(timezone=True), index=True)        # Deadline (tasks)
    period_start = Column(Date)                                  # Period-based (goals)
    period_end = Column(Date)
    
    # Context
    context_tags = Column(ARRAY(String), default=[])  # ['town', 'focus_required', 'work']
    location = Column(String(255))
    estimated_duration = Column(Interval)  # PostgreSQL interval type
    
    # State
    status = Column(String(20), default='pending', index=True)
    # Values: 'pending', 'active', 'completed', 'blocked', 'cancelled'
    completed_at = Column(DateTime(timezone=True))
    blocked_by = Column(ARRAY(UUID(as_uuid=True)), default=[])  # Other entity IDs
    
    # Metadata
    priority = Column(Integer, default=0)
    extra_data = Column(JSONB, default={})  # Flexible storage
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships

    user = relationship("User", back_populates="entities")

    parent_relations = relationship(
        "EntityRelation",
        foreign_keys="EntityRelation.child_id",
        back_populates="child",
        cascade="all, delete-orphan"
    )
    child_relations = relationship(
        "EntityRelation",
        foreign_keys="EntityRelation.parent_id",
        back_populates="parent",
        cascade="all, delete-orphan"
    )