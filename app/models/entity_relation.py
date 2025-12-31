from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.database import Base

class EntityRelation(Base):
    __tablename__ = "entity_relations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    child_id = Column(UUID(as_uuid=True), ForeignKey("entities.id", ondelete="CASCADE"), nullable=False)
    
    relation_type = Column(String(50), nullable=False)
    # Values: 'subtask', 'prerequisite', 'milestone_of', 'related_to', 'combine_with', 'blocks'
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    parent = relationship("Entity", foreign_keys=[parent_id], back_populates="child_relations")
    child = relationship("Entity", foreign_keys=[child_id], back_populates="parent_relations")