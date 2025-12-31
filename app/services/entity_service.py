from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime, date
from app.models import Entity, EntityRelation, ContextWindow
from app.schemas.entity import EntityCreate, EntityUpdate, ContextWindowCreate

class EntityService:
    
    @staticmethod
    def create_entity(db: Session, user_id: UUID, entity_data: EntityCreate) -> Entity:
        """Create a new entity"""
        entity = Entity(
            user_id=user_id,
            entity_type=entity_data.entity_type,
            title=entity_data.title,
            description=entity_data.description,
            scheduled_at=entity_data.scheduled_at,
            due_at=entity_data.due_at,
            period_start=entity_data.period_start,
            period_end=entity_data.period_end,
            context_tags=entity_data.context_tags,
            location=entity_data.location,
            estimated_duration=entity_data.estimated_duration,
            status=entity_data.status,
            priority=entity_data.priority,
            extra_data=entity_data.extra_data
        )
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity
    
    @staticmethod
    def get_user_entities(
        db: Session, 
        user_id: UUID,
        entity_type: Optional[str] = None,
        context_tag: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Entity]:
        """Get entities with optional filters"""
        query = db.query(Entity).filter(Entity.user_id == user_id)
        
        if entity_type:
            query = query.filter(Entity.entity_type == entity_type)
        
        if context_tag:
            query = query.filter(Entity.context_tags.contains([context_tag]))
        
        if status:
            query = query.filter(Entity.status == status)
        
        return query.order_by(Entity.priority.desc(), Entity.created_at.desc()).all()
    
    @staticmethod
    def get_entity_by_id(db: Session, entity_id: UUID, user_id: UUID) -> Optional[Entity]:
        """Get a specific entity"""
        return db.query(Entity).filter(
            Entity.id == entity_id,
            Entity.user_id == user_id
        ).first()
    
    @staticmethod
    def update_entity(db: Session, entity_id: UUID, user_id: UUID, entity_data: EntityUpdate) -> Entity:
        """Update an entity"""
        entity = EntityService.get_entity_by_id(db, entity_id, user_id)
        
        if not entity:
            raise ValueError("Entity not found")
        
        update_data = entity_data.model_dump(exclude_unset=True)
        
        # Handle completion
        if "status" in update_data and update_data["status"] == "completed" and not entity.completed_at:
            update_data["completed_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(entity, field, value)
        
        db.commit()
        db.refresh(entity)
        return entity
    
    @staticmethod
    def delete_entity(db: Session, entity_id: UUID, user_id: UUID) -> bool:
        """Delete an entity"""
        entity = EntityService.get_entity_by_id(db, entity_id, user_id)
        
        if not entity:
            return False
        
        db.delete(entity)
        db.commit()
        return True
    
    @staticmethod
    def create_relation(db: Session, parent_id: UUID, child_id: UUID, relation_type: str) -> EntityRelation:
        """Create a relationship between entities"""
        relation = EntityRelation(
            parent_id=parent_id,
            child_id=child_id,
            relation_type=relation_type
        )
        db.add(relation)
        db.commit()
        db.refresh(relation)
        return relation
    
    @staticmethod
    def get_entity_relations(db: Session, entity_id: UUID) -> List[EntityRelation]:
        """Get all relationships for an entity"""
        return db.query(EntityRelation).filter(
            (EntityRelation.parent_id == entity_id) | (EntityRelation.child_id == entity_id)
        ).all()
    
    @staticmethod
    def create_context_window(db: Session, user_id: UUID, window_data: ContextWindowCreate) -> ContextWindow:
        """Create a context window"""
        window = ContextWindow(
            user_id=user_id,
            window_type=window_data.window_type,
            start_time=window_data.start_time,
            end_time=window_data.end_time,
            days_of_week=window_data.days_of_week,
            energy_level=window_data.energy_level,
            preferred_activities=window_data.preferred_activities,
            extra_data=window_data.extra_data
        )
        db.add(window)
        db.commit()
        db.refresh(window)
        return window
    
    @staticmethod
    def get_user_context_windows(db: Session, user_id: UUID) -> List[ContextWindow]:
        """Get all context windows for user"""
        return db.query(ContextWindow).filter(ContextWindow.user_id == user_id).all()